#!/usr/bin/python3

import requests, sys, subprocess, argparse,  math
from datetime import datetime
from time import sleep

class Timer:
    def __init__(self):
        self.start = datetime.now()
        self.stop = None
    
    def stop_timer(self):
        self.stop = datetime.now()

    def get_start(self):
        return self.start.strftime("%H:%M:%S")

    def get_stop(self):
        return self.stop.strftime("%H:%M:%S")

def get_home_dir():
    get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return get_home_dir.stdout.replace("\n", "")

def get_fqdn_obj(args):
    r = requests.post(f'http://{args.server}:{args.port}/api/auto', data={'fqdn':args.fqdn})
    return r.json()

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-P','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('-d','--fqdn', help='Name of the root/seed FQDN', required=False)
    return parser.parse_args()

def main(args):
    starter_timer = Timer()
    sleep(2)
    starter_timer.stop_timer()
    print(f"[+] Done!  Start: {starter_timer.get_start()}  |  Stop: {starter_timer.get_stop()}")

if __name__ == "__main__":
    args = arg_parse()
    main(args)