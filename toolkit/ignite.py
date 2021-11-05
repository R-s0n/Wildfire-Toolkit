import requests, sys, subprocess, json, time, math, random, argparse, string
from datetime import datetime
from bs4 import BeautifulSoup

def wordlist_scan(args, target_url_string, blacklist=[], filter_regex="404 Not Found", wordlist="start.txt"):
    home_dir = get_home_dir()
    thisUrl = get_target_url_object(args, target_url_string)
    print(filter_regex)
    subprocess.run([f"{home_dir}/go/bin/ffuf -w '../wordlists/{wordlist}' -u {target_url_string}/FUZZ -recursion -recursion-depth 4 -timeout 3 -r -p 0.1-3.0 -sa -t 50 -fr '{filter_regex}' -fc 403 -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
    with open('/tmp/ffuf-results.tmp') as json_file:
        data = json.load(json_file)
    for result in data['results']:
        try:
            if result['input']['FUZZ'][-1] == "/":
                result_data = {"endpoint":result['input']['FUZZ'][:-1], "statusCode":result['status'], "responseLength":result['length']}
            else:
                result_data = {"endpoint":result['input']['FUZZ'], "statusCode":result['status'], "responseLength":result['length']}
        except Exception as e:
            # print(f"[!] EXCEPTION: {e}")
            continue
        if len(result_data['endpoint']) < 1:
            result_data['endpoint'] = "/"
        if result_data['endpoint'][0] != "/":
            result_data['endpoint'] = f"/{result_data['endpoint']}"
        if '?' in result_data['endpoint']:
            temp = result_data['endpoint'].split('?')
            result_data['endpoint'] = temp[0]
        result_str = result_data['endpoint']
        current_endpoints_list = []
        current_endpoints = thisUrl['endpoints']
        for endpoint in current_endpoints:
            current_endpoints_list.append(endpoint['endpoint'])
        if result_str not in current_endpoints_list or ".png" not in result_str or ".PNG" not in result_str or ".jpg" not in result_str or ".JPG" not in result_str:
            thisUrl['endpoints'].append(result_data)
    update_url(args, thisUrl)

def wordlist_scan_files(args, target_url_string, blacklist=[], filter_regex="404 Not Found"):
    thisUrl = get_target_url_object(args, target_url_string)
    endpoint_list = []
    endpoints = thisUrl['endpoints']
    for endpoint in endpoints:
        endpoint_list.append(endpoint['endpoint'])
    home_dir = get_home_dir()
    for endpoint in endpoint_list:
        skip = False
        for blacklisted_endpoint in blacklist:
            if blacklisted_endpoint == endpoint:
                skip = True
        if skip == True:
            continue
        if "." in endpoint[-6:] and ".com" not in endpoint[-6:]:
            print("Skipping File...")
            print(endpoint)
            continue
        subprocess.run([f"{home_dir}/go/bin/ffuf -w '../wordlists/files.txt' -u {target_url_string}{endpoint}/FUZZ -recursion -recursion-depth 4 -timeout 3 -r -p 0.1-3.0 -sa -t 50 -fr '{filter_regex}' -fc 403 -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
        with open('/tmp/ffuf-results.tmp') as json_file:
            data = json.load(json_file)
        for result in data['results']:
            if result['input']['FUZZ'][-1] == "/":
                result_data = {"endpoint":result['input']['FUZZ'][:-1], "statusCode":result['status'], "responseLength":result['length']}
            else:
                result_data = {"endpoint":result['input']['FUZZ'], "statusCode":result['status'], "responseLength":result['length']}
            if len(result_data['endpoint']) < 1:
                result_data['endpoint'] = "/"
            if result_data['endpoint'][0] != "/":
                result_data['endpoint'] = f"/{result_data['endpoint']}"
            result_str = result_data['endpoint']
            current_endpoints_list = []
            current_endpoints = thisUrl['endpoints']
            for endpoint in current_endpoints:
                current_endpoints_list.append(endpoint['endpoint'])
            if '?' in result_data['endpoint']:
                temp = result_data['endpoint'].split('?')
                result_data['endpoint'] = temp[0]
            if result_str not in current_endpoints_list or ".png" not in result_str or ".PNG" not in result_str or ".jpg" not in result_str or ".JPG" not in result_str:
                thisUrl['endpoints'].append(result_data)
        wordlist_len = len(thisUrl['completedWordlists'])
        update_url(args, thisUrl)

def crawl_scan(args, target_url_string, blacklist=[], filter_regex="404 Not Found"):
    thisUrl = get_target_url_object(args, target_url_string)
    url_list = [f"{target_url_string}/"]
    for endpoint in thisUrl['endpoints']:
        url_list.append(f"{target_url_string}{endpoint['endpoint']}")
    print("url_list: ")
    print(url_list)
    for url in url_list:
        skip = False
        for blacklisted_endpoint in blacklist:
            if f"{target_url_string}{blacklisted_endpoint}" == url:
                skip = True
                print(f"[!] Endpoint {blacklisted_endpoint} is blacklisted.")
        if skip == True:
            print("[!] Skipping blacklisted endpoint...")
            continue
        if "." in url[-6:] and ".com" not in url[-6:]:
            print(f"[!] Skipping File {url}...")
            continue
        print(f"Testing {url}")
        length = len(target_url_string) + 1
        prefix = url[length:]
        print(f"Prefix: {prefix}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.findAll('a')
        for link in links:
            try:
                href = link['href']
            except Exception as e:
                continue
            if "http" in href:
                if target_url_string in href:
                    url_length = len(target_url_string)
                    path = href[url_length:].split("/")
                    path_list = []
                    for p in path:
                        if len(p) < 1:
                            path.remove(p)
                        else:
                            print(p)
                            result_data = {"endpoint":p, "statusCode":000, "responseLength":000}
                            current_endpoints_list = []
                            current_endpoints = thisUrl['endpoints']
                            for endpoint in current_endpoints:
                                current_endpoints_list.append(endpoint['endpoint'])
                            if p not in current_endpoints_list:
                                thisUrl['endpoints'].append(result_data)
            else:
                print(href)
                if href[0] == "/":
                    result_data = {"endpoint":href, "statusCode":000, "responseLength":000}
                else:
                    result_data = {"endpoint":f"/{href}", "statusCode":000, "responseLength":000}
                current_endpoints_list = []
                current_endpoints = thisUrl['endpoints']
                for endpoint in current_endpoints:
                    current_endpoints_list.append(endpoint['endpoint'])
                if href not in current_endpoints_list:
                    thisUrl['endpoints'].append(result_data)
        write_wordlist(args, thisUrl)
        home_dir = get_home_dir()
        subprocess.run([f"{home_dir}/go/bin/ffuf -w '../wordlists/crawl_wordlist_{args.domain}.txt' -u {url}FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '{filter_regex}' -fc 403 -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
        thisUrl = get_target_url_object(args, target_url_string)
        with open('/tmp/ffuf-results.tmp') as json_file:
            data = json.load(json_file)
        for result in data['results']:
            try:
                if result['input']['FUZZ'][-1] == "/":
                    result_data = {"endpoint":prefix + result['input']['FUZZ'][:-1], "statusCode":result['status'], "responseLength":result['length']}
                else:
                    result_data = {"endpoint":prefix + result['input']['FUZZ'], "statusCode":result['status'], "responseLength":result['length']}
            except:
                continue
            print(result_data['endpoint'])
            if len(result_data['endpoint']) < 1:
                result_data['endpoint'] = "/"
            if result_data['endpoint'][0] != "/":
                result_data['endpoint'] = f"/{result_data['endpoint']}"
            if '?' in result_data['endpoint']:
                temp = result_data['endpoint'].split('?')
                result_data['endpoint'] = temp[0]
            result_str = result_data['endpoint']
            current_endpoints_list = []
            current_endpoints = thisUrl['endpoints']
            for endpoint in current_endpoints:
                current_endpoints_list.append(endpoint['endpoint'])
            if '#' not in result_data['endpoint'] and result_str not in current_endpoints_list and ".png" not in result_str and ".PNG" not in result_str and ".jpg" not in result_str and ".JPG" not in result_str:
                thisUrl['endpoints'].append(result_data)
        update_url(args, thisUrl)


def cewl_scan(args, target_url_string, blacklist=[], filter_regex="404 Not Found"):
    home_dir = get_home_dir()
    thisUrl = get_target_url_object(args, target_url_string)
    print("[-] Generating custom wordlist...")
    subprocess.run([f'cewl -d 2 -m 5 -o -a -w {home_dir}/Wordlists/{args.domain}_custom.txt {target_url_string}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    print("[-] Enumerating endpoints using custom wordlist...")
    subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/{args.domain}_custom.txt' -u {target_url_string}/FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '{filter_regex}' -fc 403 -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
    with open('/tmp/ffuf-results.tmp') as json_file:
        data = json.load(json_file)
    for result in data['results']:
        result_data = {"endpoint":result['input']['FUZZ'], "statusCode":result['status'], "responseLength":result['length']}
        if len(result_data['endpoint']) < 1:
            result_data['endpoint'] = "/"
        if result_data['endpoint'][0] != "/":
            result_data['endpoint'] = f"/{result_data['endpoint']}"
        result_str = result_data['endpoint']
        current_endpoints_list = []
        current_endpoints = thisUrl['endpoints']
        for endpoint in current_endpoints:
            current_endpoints_list.append(endpoint['endpoint'])
        if '?' not in result_data['endpoint'] and '#' not in result_data['endpoint'] and result_str not in current_endpoints_list:
            thisUrl['endpoints'].append(result_data)
    thisUrl['completedWordlists'].append("cewl")
    update_url(args, thisUrl)

def remove_duplicates(args, target_url_string):
    thisUrl = get_target_url_object(args, target_url_string)
    endpoints = []
    new_url_endpoints = []
    for endpoint in thisUrl['endpoints']:
        try:
            if endpoint['endpoint'][-1] == "/":
                endpoint['endpoint'] = endpoint['endpoint'][:-1]
            if endpoint['endpoint'] in endpoints:
                continue
            else:
                new_url_endpoints.append(endpoint)
                endpoints.append(endpoint['endpoint'])
        except Exception as e:
            # print(e)
            continue
    thisUrl['endpoints'] = new_url_endpoints
    update_url(args, thisUrl)
    
def random_string(size=50, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def check_thisdoesnotexist(args, target_url_string):
    rand_string = random_string()
    res = requests.get(f"{target_url_string}/{rand_string}")
    if res.status_code != 404:
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            if soup.title != None:
                return soup.title
        except Exception as e:
            return res.text
    return "404 Not Found"

def check_dynamic_routing(args, target_url_string):
    thisUrl = get_target_url_object(args, target_url_string)
    endpoint_list = []
    for endpoint in thisUrl['endpoints']:
        endpoint_list.append(endpoint['endpoint'])
    rand_string = random_string()
    blacklist = []
    for endpoint in endpoint_list:
        try:
            res = requests.get(f"{target_url_string}{endpoint}/{rand_string}")
            if res.status_code == 200:
                print(f"[!] {endpoint} appears to be dynamic.  Adding to blacklist...")
                blacklist.append(endpoint)
        except Exception as e:
            # print(e)
            blacklist.append(endpoint)
    return blacklist

def final_status_check(args, target_url_string):
    thisUrl = get_target_url_object(args, target_url_string)
    endpoints = []
    new_url_endpoints = []
    for endpoint in thisUrl['endpoints']:
        try:
            endpoint_string = endpoint['endpoint']
            res = requests.get(f"{target_url_string}{endpoint_string}")
            if res.status_code != 404:
                new_url_endpoints.append(endpoint)
        except Exception as e:
            # print(e)
            continue
    thisUrl['endpoints'] = new_url_endpoints
    update_url(args, thisUrl)

def write_wordlist(args, thisUrl):
    f = open(f'../wordlists/crawl_wordlist_{args.domain}.txt', 'w')
    for endpoint in thisUrl['endpoints']:
        f.write(f"{endpoint['endpoint']}\n")
    f.close()

def delete_wordlists():
    subprocess.run(["rm ../wordlists/crawl_wordlist_*"], shell=True)

def update_url(args, thisUrl):
    res = requests.post(f'http://{args.server}:{args.port}/api/url/auto/update', json=thisUrl, headers={'Content-type':'application/json'}, proxies={'http':f'http://{args.proxy}:8080'})

def get_target_url_object(args, target_url_string):
    r = requests.post(f'http://{args.server}:{args.port}/api/url/auto', data={'url':target_url_string})
    return r.json()

def get_target_url_string(args):
    r = requests.post(f'http://{args.server}:{args.port}/api/auto', data={'fqdn':args.domain})
    thisFqdn = r.json()
    return thisFqdn['targetUrls'][0]

def get_home_dir():
    get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return get_home_dir.stdout.replace("\n", "")

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--domain', help='FQDN of Target URL', required=True)
    parser.add_argument('-p','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('-s','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-P','--proxy', help='IP Address of Burp Suite Proxy', required=False)
    parser.add_argument('-t','--targeted', help='Run Targeted Scan (Small, Pre-Set Wordlist)', required=False, action='store_true')
    return parser.parse_args()

def main(args):
    target_url_string = get_target_url_string(args)
    print(f"[-] Enumerating endpoints on {target_url_string}")
    print("[-] Checking for custom 404 page...")
    filter_regex = check_thisdoesnotexist(args, target_url_string)
    if filter_regex == "404 Not Found":
        print("[+] Custom 404 page was NOT detected.  Continuing...")
    else:
        print("[!] Custom 404 page detected!  Adding REGEX filter...")
    print("[-] Performing initial wordlist scan...")
    blacklist = []
    wordlist_scan(args, target_url_string, blacklist, filter_regex)
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    print("blacklist: ")
    print(blacklist)
    print("[-] Performing crawl scan...")
    crawl_scan(args, target_url_string, blacklist, filter_regex)
    print("[-] Cleaning up the data...")
    remove_duplicates(args, target_url_string)
    print("[-] Performing deeper wordlist scan...")
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    wordlist = "deep.txt"
    wordlist_scan(args, target_url_string, blacklist, filter_regex, wordlist)
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    print("[-] Performing crawl scan...")
    crawl_scan(args, target_url_string, blacklist, filter_regex)
    print("[-] Cleaning up the data...")
    remove_duplicates(args, target_url_string)
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    print("[-] Performing file scan on all endpoints...")
    wordlist_scan_files(args, target_url_string, blacklist, filter_regex)
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    print("[-] Cleaning up the data...")
    remove_duplicates(args, target_url_string)
    print("[-] Performing crawl scan...")
    crawl_scan(args, target_url_string, blacklist, filter_regex)
    print("[-] Checking for endpoints with dynamic routing...")
    blacklist = check_dynamic_routing(args, target_url_string)
    print("[-] Cleaning up the data...")
    remove_duplicates(args, target_url_string)  
    # Add javascript crawl using javasoup
    crawl_scan(args, target_url_string, blacklist, filter_regex)
    print("[-] Performing final cleanup...")
    remove_duplicates(args, target_url_string)
    delete_wordlists()
    final_status_check(args, target_url_string)
    print(f"[+] Ignite.py completed successfully!")

if __name__ == "__main__":
    args = arg_parse()
    main(args)