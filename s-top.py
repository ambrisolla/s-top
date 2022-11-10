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
from operator import itemgetter

class STop:
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
             ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora
nt(f"{barcolor}█\033[0m", end="")
            essh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora

             ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora
nt(" ", end="")
        printssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora
}%]".format(swap_perc_usage), end="\n")
        printssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora

            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora
;30m\033[47m{: <10}{: <15}{: <10}{: <15}{: <30}\033[0m".format(
             ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora
D", "USER", "%USAGE", "USAGE in kB", "COMMAND"
            )ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDgmkrofl1+jgZkfV+/dX4ZTduDC4aULboyJOWMZvQbKuDcbzV8wY5x9QzCJO6l5ndJjFzJNww2UzbFsH9C2lP2VV8PbF179J5ODsjsBzUxS2Jla1ctOJVsJX7pvCLC8iyqLpMaE3JhDADI+nSREv+0xZYfAoldaVgLYPXKzX06CzXu1VEmKCjVmf3BOC7PSNv87SiRmNTDBeVAD7u79oikWRfELG/ZOprxNFJGxX8ytnkAbYM3JDYyY+AQaKdFFtbT6IG2cGhCXUNUEbdVPj1rdOdgg6O0f0TLe7i58gf2sCZHHtswLoQ8Ne5n2yxK1E/naaSbA82aVAYs4A43b/h/+vXwKJcx5Fdhu6zdU5Awv6soKkQBII+a/5SxqH8EyA0/ooCmwTPzctWq9K3ahb2Bk1Yt64J4wjuXu015LmDQiAuyod82m48TcC09TryUkwV02XPtY9e0Ov52KYUwovC5Hlq8oJo/+EMtYzsWj7B1l99Jf9cK8MpT84ctgEdz5i0= andre@fedora

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


s = STop()
s.run()
