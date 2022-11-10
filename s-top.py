#!/usr/bin/env python

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
from operator import itemgetter

class Swapper:
    def __init__(self):
        swap_info = self.get_swap_info()
        self.SwapTotal = swap_info["SwapTotal"]
        self.users = self.get_users()

    def get_users(self):
        try:
            cmd = "cat /etc/passwd"
            run = sb.run(cmd, shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
            if run.returncode != 0:
                print(f"Erro: {run.stderr.decode()}")
                sys.exit(1)
            else:
                passwd = run.stdout.decode().split("\n")
                data = [
                    {"username": x.split(":")[0], "uid": int(x.split(":")[2])}
                    for x in passwd
                    if x
                ]
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
                output_parsed = [re.sub("\s+|[K,k][B,b]$", "", x) for x in output if x]
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
                        swap_consumed = re.sub('VmSwap:\t\s+|[" "]kB', "", item).split(
                            ":"
                        )[1]
                        percent = float((int(swap_consumed) / self.SwapTotal) * 100)
                        percent_parsed = f"{percent:.1f}"
                        pids.append(
                            {
                                "pid": int(pid),
                                "name": name,
                                "swap_consumed": int(swap_consumed),
                                "percent": float(percent_parsed),
                                "uid": uid,
                            }
                        )
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
        swap_perc_usage = int(
            ((swap_info["SwapTotal"] - swap_info["SwapFree"]) / swap_info["SwapTotal"])
            * 100
        )
        print("{:<20}".format("Swap percent usage  : |"), end="")
        for a in range(0, 50):
            if a <= swap_perc_usage / 2:
                if swap_perc_usage < 80:
                    barcolor = "\033[0;32m"
                elif swap_perc_usage >= 80 and swap_perc_usage < 90:
                    barcolor = "\033[93m"
                elif swap_perc_usage >= 90:
                    barcolor = "\033[91m"
                print(f"{barcolor}█\033[0m", end="")
            else:
                print(" ", end="")
        print("| [{}%]".format(swap_perc_usage), end="\n")
        print(
            "\033[0;30m\033[47m{: <10}{: <15}{: <10}{: <15}{: <30}\033[0m".format(
                "PID", "USER", "%USAGE", "USAGE in kB", "COMMAND"
            )
        )
        itens_to_show = 20
        for idx, proc in enumerate(data):
            pid = proc["pid"]
            try:
                username = [
                    x["username"] for x in self.users if x["uid"] == int(proc["uid"])
                ][0]
            except:
                username = proc["uid"]
            name = proc["name"]
            swap_consumed = proc["swap_consumed"]
            percent = proc["percent"]
            if idx <= itens_to_show:
                print(
                    "{: <10}{: <15}{: <10}{: <15}{: <20}".format(
                        pid, username, percent, swap_consumed, name
                    )
                )

    def run(self):
        while True:
            self.display_data()
            time.sleep(5)


s = Swapper()
s.run()
