#!/usr/bin/python3

import requests, argparse, subprocess, sys, json
from datetime import datetime

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

def get_fqdns(args):
    res = requests.post(f"http://{args.server}:{args.port}/api/fqdn/all")
    return res

def sort_fqdns(fqdns):
    sorted_fqdns = []
    while len(fqdns) > 0:
        last_updated = fqdns[0]
        for fqdn in fqdns:
            if last_updated['updatedAt'] > fqdn['updatedAt']:
                last_updated = fqdn
        fqdns.remove(last_updated)
        sorted_fqdns.append(last_updated)
    return sorted_fqdns

def start(args):
    res = get_fqdns(args)
    fqdn_json = json.loads(res.text)
    sorted_fqdns = sort_fqdns(fqdn_json)
    for fqdn in sorted_fqdns:
        if fqdn['fqdn'] != args.blacklist:
            seed = fqdn['fqdn']
            print(f"[-] Running Fire-Starter Modules (Subdomain Recon) against {seed}")
            subprocess.run([f'python3 toolkit/fire_starter.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
            subprocess.run([f'python3 toolkit/clear_sky.py -d {seed} -s {args.server} -p {args.port}'], shell=True)
            subprocess.run([f'python3 toolkit/kindling.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
        else:
            print(f"[!] {fqdn['fqdn']} has been blacklisted for this round of scanning.  Skipping...")
    return True

def spread(args):
    res = get_fqdns(args)
    fqdn_json = json.loads(res.text)
    sorted_fqdns = sort_fqdns(fqdn_json)
    for fqdn in sorted_fqdns:
        if fqdn['fqdn'] != args.blacklist:
            seed = fqdn['fqdn']
            print(f"[-] Running Fire-Spreader Modules (Server/Port Recon) against {seed}")
            subprocess.run([f'python3 toolkit/firewood.py -d {seed} -s {args.server} -p {args.port}'], shell=True)
            subprocess.run([f'python3 toolkit/wind.py -d {seed} -s {args.server} -p {args.port}'], shell=True)
        else:
            print(f"[!] {fqdn['fqdn']} has been blacklisted for this round of scanning.  Skipping...")
    return True

def scan(args):
    res = get_fqdns(args)
    fqdn_json = json.loads(res.text)
    sorted_fqdns = sort_fqdns(fqdn_json)
    for fqdn in sorted_fqdns:
        if fqdn['fqdn'] != args.blacklist:
            seed = fqdn['fqdn']
            print(f"[-] Running Drifting-Embers Modules (Vuln Scanning) against {seed}")
            subprocess.run([f'python3 toolkit/nuclei_embers.py -d {seed} -s {args.server} -p {args.port} -t ~/nuclei-templates'], shell=True)
            # subprocess.run([f'python3 toolkit/proto_pollution_embers.py -d {seed} -s {args.server} -p {args.port} -T 2'], shell=True)
            # subprocess.run([f'python3 toolkit/cve_embers.py -D {seed} -S {args.server} -P {args.port} -j -d 1'], shell=True)
        else:
            print(f"[!] {fqdn['fqdn']} has been blacklisted for this round of scanning.  Skipping...")
    return True

def enum(args):
    res = get_fqdns(args)
    fqdn_json = json.loads(res.text)
    sorted_fqdns = sort_fqdns(fqdn_json)
    for fqdn in sorted_fqdns:
        if fqdn['fqdn'] != args.blacklist:
            seed = fqdn['fqdn']
            print(f"[-] Running Enumeration Modules against {seed}")
            subprocess.run([f'python3 toolkit/ignite.py -d {seed} -s {args.server} -p {args.port} -P {args.proxy} -t'], shell=True)
            # subprocess.run([f'python3 toolkit/engulf.py -d {seed} -s {args.server} -p {args.port} -T 2'], shell=True)
        else:
            print(f"[!] {fqdn['fqdn']} has been blacklisted for this round of scanning.  Skipping...")
    return True

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-P','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('-p','--proxy', help='IP Address of Burp Suite Proxy', required=False)
    parser.add_argument('-b','--blacklist', help='FQDN to Blacklist (skip) for this round of testing', required=False)
    parser.add_argument('--start', help='Run Fire-Starter Modules', required=False, action='store_true')
    parser.add_argument('--spread', help='Run Fire-Spreader Modules (Expect a LONG scan time)', required=False, action='store_true')
    parser.add_argument('--scan', help='Run Vuln Scan Modules', required=False, action='store_true')
    parser.add_argument('--enum', help='Run Enumeration Modules', required=False, action='store_true')
    return parser.parse_args()

def main(args):
    wildfire_timer = Timer()
    if args.start is True and args.spread is True:
        start(args)
        spread(args)
    elif args.start is True and args.spread is False:
        start(args)
    elif args.spread is True and args.start is False:
        spread(args)
    if args.scan is True:
        scan(args)
    if not args.proxy:
        args.proxy = "127.0.0.1"
    if args.enum is True:
        enum(args)
    if args.start is False and args.spread is False and args.scan is False and args.enum is False:
        print("[!] Please Choose a Module!\n[!] Options:\n\n   --start   [Run Fire-Starter Modules]\n   --spread  [Run Fire-Spreader Modules] (Expect a LONG scan time)\n   --scan    [Run Vuln Scan Modules]\n   --enum    [Run Enumeration Modules]\n")
    wildfire_timer.stop_timer()
    print(f"[+] Done!  Start: {wildfire_timer.get_start()}  |  Stop: {wildfire_timer.get_stop()}")

if __name__ == "__main__":
    args = arg_parse()
    main(args)