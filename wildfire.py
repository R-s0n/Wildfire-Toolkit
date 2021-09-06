
import requests, argparse, subprocess, sys, json

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
        seed = fqdn['fqdn']
        subprocess.run([f'python3 toolkit/fire_starter.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
        subprocess.run([f'python3 toolkit/kindling.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
    return True

def spread(args):
    res = get_fqdns(args)
    fqdn_json = json.loads(res.text)
    sorted_fqdns = sort_fqdns(fqdn_json)
    for fqdn in sorted_fqdns:
        seed = fqdn['fqdn']
        subprocess.run([f'python3 toolkit/firewood.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
        subprocess.run([f'python3 toolkit/wind.py -d {seed} -s {args.server} -p {args.port} '], shell=True)
    return True

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-P','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('--start', help='Run Fire-Starter Modules', required=False, action='store_true')
    parser.add_argument('--spread', help='Run Fire-Spreader Modules (Expect a LONG scan time)', required=False, action='store_true')
    return parser.parse_args()

def main(args):
    if args.start is True and args.spread is True:
        start(args)
        spread(args)
    if args.start is True:
        start(args)
    if args.spread is True:
        spread(args)
    if args.start is False and args.spread is False:
        print("[!] Please Choose a Module!\n[!] Options:\n\n   --start   [Run Fire-Starter Modules]\n   --spread  [Run Fire-Spreader Modules] (Expect a LONG scan time)\n   --scan    [Run Vuln Scan Modules]\n")
    print("[+] Done!")

if __name__ == "__main__":
    args = arg_parse()
    main(args)