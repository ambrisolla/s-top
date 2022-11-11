#!/usr/bin/env python3

"""
	Developed by Andre Muzel Brisolla
	Nov 10, 2022
"""

import json
import os
import re
import sys
import time
import subprocess as sb
from   operator import itemgetter


class STop:
  
  def __init__(self):
    swap_info                 = self.get_swap_info()
    self.SwapTotal            = swap_info["SwapTotal"]
    self.users                = self.get_users()
    # set colors
    self.shell_green          = '\033[0;32m'
    self.shell_yellow         = '\033[93m'
    self.shell_red            = '\033[91m'
    self.shell_white          = '\033[0;30m'
    self.shell_black          = '\033[47m'
    self.shell_color_finished = '\033[0m' 
    

  def get_users(self):
    try:
      cmd = "cat /etc/passwd"
      run = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
      if run.returncode != 0:
        print(f"Erro: {run.stderr.decode()}")
        sys.exit(1)
      else:
        passwd = run.stdout.decode().split("\n")
        data = [{"username": x.split(":")[0], "uid": int(x.split(":")[2])} for x in passwd if x]
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
        output_parsed = [ re.sub("\s+|[K,k][B,b]$", "", x)for x in output if x ]
        output_data = {}
        for item in output_parsed:
          key = item.split(":")[0]
          value = item.split(":")[1]
          output_data[key] = int(value)
      return output_data
    except Exception as err:
      print(f"Error: {str(err)}")
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
            pid = item.split("/")[2]
            if re.search(f"{pid}.*Name", item):
              name = item.split("\t")[-1]
            if re.search(f"{pid}.*Uid", item):
              uids = item.split("Uid:")[1]
              uid = re.sub("\t", ",", uids).split(",")[1]
            if re.search(f"{pid}.*VmSwap", item):
              swap_consumed = re.sub('VmSwap:\t\s+|[" "]kB', "", item).split(":")[1]
              percent = float((int(swap_consumed) / self.SwapTotal) * 100)
              percent_parsed = f"{percent:.1f}"
              pids.append({
                "pid": int(pid),
                "name": name,
                "swap_consumed": int(swap_consumed),
                "percent": float(percent_parsed),
                "uid": uid
                })
      return pids
    except Exception as err:
      print(f"Error: {str(err)}")
      sys.exit(1)

  def sort_by(self, **kwargs):
    data = self.get_data()
    if "sort_by" not in kwargs or kwargs["sort_by"] == "":
      sort_by = "swap_consumed"
    else:
      sort_by = kwargs["sort_by"]
    data_sorted = sorted(data, key=itemgetter(sort_by), reverse=True)
    return data_sorted

  def display_data(self):
    data = self.sort_by(sort_by="")
    swap_info = dict(
      [[x, self.get_swap_info().get(x)] for x in self.get_swap_info()]
    )
    # clear screen
    os.system("clear")
    for info in swap_info:
      key = "{}".format(info)
      value = ": {} kB".format(swap_info[info])
      print("{: <20}{: <20} ".format(key, value))
    swap_perc_usage = int((( swap_info["SwapTotal"] - swap_info["SwapFree"]) / swap_info["SwapTotal"] ) * 100 )
    print("{:<20}".format("Swap percent usage  : |"), end="")
    #
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
             "PID", "USER", "%USAGE", "USAGE in kB", "COMMAND", 
             self.shell_color_finished))
    itens_to_show = 20
    for idx, proc in enumerate(data):
      pid = proc["pid"]
      try:
        username = [ x["username"] for x in self.users if x["uid"] == int(proc["uid"]) ][0]
      except:
        username = proc["uid"]
      name          = proc["name"]
      swap_consumed = proc["swap_consumed"]
      percent       = proc["percent"]
      if idx <= itens_to_show:
        print("{:<10}{:<15}{:<10}{:<15}{:<20}".
          format(pid, username, percent, swap_consumed, name))

  def run(self):
      while True:
          self.display_data()
          time.sleep(5)


s = STop()
s.run()
