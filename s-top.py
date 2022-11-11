#!/usr/bin/env python3

"""
  Developed by Andre Muzel Brisolla
  Nov 10, 2022
"""

import os
import re
import sys
import time
import subprocess as sb
import argparse
from   operator import itemgetter

class STop:
  
  def __init__(self, **kwargs):
    swap_info                 = self.get_swap_info()
    self.SwapTotal            = swap_info['SwapTotal']
    self.users                = self.get_users()
    # settings
    self.procs_to_show        = 20
    # set colors
    self.shell_green          = '\033[0;32m'
    self.shell_yellow         = '\033[93m'
    self.shell_red            = '\033[91m'
    self.shell_white          = '\033[0;30m'
    self.shell_black          = '\033[47m'
    self.shell_color_finished = '\033[0m' 
    # sort settings
    self.sort_reversed        = kwargs['reversed']
    self.sort_by              = kwargs['sort_by']
    
  def get_users(self):
    try:
      cmd = 'cat /etc/passwd'
      run = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
      if run.returncode != 0:
        print(f'Erro: {run.stderr.decode()}')
        sys.exit(1)
      else:
        passwd = run.stdout.decode().split('\n')
        data = [ {'username' : x.split(':')[0], 'uid': int(x.split(':')[2])} for x in passwd if x ]
      return data
    except Exception as err:
      print(f"Error: {str(err)}")
      sys.exit(1)

  def get_swap_info(self):
    try:
      cmd = 'grep -i "swap" /proc/meminfo'
      run = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
      if run.returncode != 0:
        print(f"Erro: {run.stderr.decode()}")
        sys.exit(1)
      else:
        output = run.stdout.decode().split("\n")
        output_parsed = [ re.sub('\s+|[K,k][B,b]$', '', x)for x in output if x ]
        output_data = {}
        for item in output_parsed:
          key = item.split(':')[0]
          value = item.split(':')[1]
          output_data[key] = int(value)
      return output_data
    except Exception as err:
      print(f'Error: {str(err)}')
      sys.exit(1)

  def get_data(self):
    try:
      cmd = 'egrep -i "vmswap|^name|^uid" /proc/[1-9]*/status'
      run = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
      if run.returncode != 0:
        print(f"Erro: {run.stderr.decode()}")
        sys.exit(1)
      else:
        output = run.stdout.decode().split("\n")
        pids = []
        for item in output:
          if item:
            pid = item.split('/')[2]
            if re.search(f'{pid}.*Name', item):
              name = item.split("\t")[-1]
            if re.search(f'{pid}.*Uid', item):
              uids = item.split('Uid:')[1]
              uid = re.sub('\t', ',', uids).split(',')[1]
            if re.search(f"{pid}.*VmSwap", item):
              usage = re.sub('VmSwap:\t\s+|[" "]kB', '', item).split(':')[1]
              percent = float((int(usage) / self.SwapTotal) * 100)
              percent_parsed = f'{percent:.1f}'
              pids.append({
                'pid': int(pid),
                'name': name,
                'usage': int(usage),
                'percent': float(percent_parsed),
                'uid': uid
                })
      return pids
    except Exception as err:
      print(f"Error: {str(err)}")
      sys.exit(1)

  def sort(self, **kwargs):
    data = self.get_data()
    if 'sort_by' not in kwargs or kwargs['sort_by'] == '':
      sort_by = 'usage'
    else:
      sort_by = kwargs['sort_by']
    data_sorted = sorted(data, key=itemgetter(sort_by), reverse=self.sort_reversed)
    return data_sorted

  def display_data(self):
    data = self.sort(sort_by=self.sort_by)
    swap_info = dict([[ x, self.get_swap_info().get(x)] for x in self.get_swap_info()])
    os.system("clear")
    for info in swap_info:
      key = "{}".format(info)
      value = ": {} kB".format(swap_info[info])
      print("{: <20}{: <20} ".format(key, value))
    swap_perc_usage = int((( swap_info['SwapTotal'] - swap_info['SwapFree']) / swap_info['SwapTotal'] ) * 100 )
    print('{:<20}'.format('Swap percent usage  : |'), end='')
    for a in range(0, 50):
      if a <= swap_perc_usage / 2:
        if swap_perc_usage < 80:
          barcolor = self.shell_green
        elif swap_perc_usage >= 80 and swap_perc_usage < 90:
          barcolor = self.shell_yellow
        elif swap_perc_usage >= 90:
          barcolor = self.shell_red
        print(f"{barcolor}█{self.shell_color_finished}", end="")
      else:
        print(" ", end="")
    print("| [{}%]".format(swap_perc_usage), end="\n")
    print("{}{}{:<10}{:<15}{:<10}{:<15}{:<30}{}".
      format(self.shell_white, 
             self.shell_black,
             'PID', 'USER', '%USAGE', 'USAGE in kB', 'COMMAND', 
             self.shell_color_finished))
    for idx, proc in enumerate(data):
      pid = proc['pid']
      try:
        username = [ x['username'] for x in self.users if x['uid'] == int(proc['uid']) ][0]
      except:
        username = proc['uid']
      name          = proc['name']
      usage = proc['usage']
      percent       = proc['percent']
      if idx <= self.procs_to_show:
        print('{:<10}{:<15}{:<10}{:<15}{:<20}'.
          format(pid, username, percent, usage, name))

  def run(self):
    while True:
      self.display_data()
      time.sleep(5)

if __name__ == '__main__':
  args = argparse.ArgumentParser()
  args.add_argument('-s', '--sort-by',  help='Sort by column', choices=['name','pid','usage'])
  args.add_argument('-a', '--asc-sort', help='Asc sort ( default is desc )', action='store_true')
  parsed = vars(args.parse_args())
  sort_by = parsed['sort_by']
  if sort_by == None:
    sort_by = ''
  if sort_by == 'user':
    sort_by = 'uid'
  if parsed['asc_sort']:
    sort_reverse = False
  else:
    sort_reverse = True
  s = STop(reversed=sort_reverse, sort_by=sort_by)
  s.run()