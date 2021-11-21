#!/usr/bin/python3

import subprocess, argparse
from wildfire import Timer
from time import sleep

def arg_parse():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    return parser.parse_args()

def main(args):
    starter_timer = Timer()
    sleep(2)
    starter_timer.stop_timer()
    print(f"[+] Done!  Start: {starter_timer.get_start()}  |  Stop: {starter_timer.get_stop()}")

if __name__ == "__main__":
    args = arg_parse()
    main(args)