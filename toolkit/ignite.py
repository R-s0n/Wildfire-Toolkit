import requests, sys, subprocess, json, time, math, random, argparse
from datetime import datetime
from bs4 import BeautifulSoup

def get_wordlists(args):
    home_dir = get_home_dir()
    if args.targeted:
        wordlist_arr = ["raft-large-directories.txt","raft-small-words.txt","api/api-endpoints.txt","api/api-seen-in-wild.txt","PHP.fuzz.txt","CMS/Django.txt","CMS/wp-plugins.fuzz.txt","raft-small-files.txt","raft-small-directories.txt"]
        # Test Wordlist List: wordlist_arr = ["PHP.fuzz.txt"]
    else:
        wordlists = subprocess.run([f"ls {home_dir}/Wordlists/SecLists/Discovery/Web-Content/"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        wordlist_arr = wordlists.stdout.split('\n')
        wordlist_arr.pop()
        dir_arr = []
        for wordlist in wordlist_arr:
            if wordlist[-4:] != ".txt":
                dir_arr.append(wordlist)
                i = wordlist_arr.index(wordlist)
                del wordlist_arr[i]
        for directory in dir_arr:
            dir_str = subprocess.run([f"ls {home_dir}/Wordlists/SecLists/Discovery/Web-Content/{directory}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
            dir_arr_temp = dir_str.stdout.split('\n')
            dir_arr_temp.pop()
            for sub_wordlist in dir_arr_temp:
                if sub_wordlist[-4:] == ".txt":
                    wordlist_arr.append(f"{directory}/{sub_wordlist}")
    return wordlist_arr

def wordlist_scan(args, wordlist_arr, target_url_string):
    home_dir = get_home_dir()
    l = len(wordlist_arr)
    wordlist_check = requests.post(f'http://{args.server}:{args.port}/api/url/auto', data={'url':target_url_string})
    wordlist_check_data = wordlist_check.json()
    wordlist_len = len(wordlist_check_data['completedWordlists'])
    while wordlist_len < l:
        thisUrl = get_target_url_object(args, target_url_string)
        print(f"[-] {wordlist_len} out of {l} wordlists attempted...")
        thisUrl = get_target_url_object(args, target_url_string)
        wordlist = random.choice(wordlist_arr)
        if wordlist in thisUrl['completedWordlists']:
            i = wordlist_arr.index(wordlist)
            del wordlist_arr[i]
            continue
        thisUrl['completedWordlists'].append(wordlist)
        format_test = subprocess.run([f"head -n 1 '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        if format_test.stdout[0] == "/":
            subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url_string}FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '404 Not Found' -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
        else:
            subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url_string}/FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '404 Not Found' -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
        i = wordlist_arr.index(wordlist)
        del wordlist_arr[i]
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
        wordlist_len = len(thisUrl['completedWordlists'])
        update_url(args, thisUrl)

def cewl_scan(args, target_url_string):
    home_dir = get_home_dir()
    thisUrl = get_target_url_object(args, target_url_string)
    if "cewl" not in thisUrl['completedWordlists']:
        print("[-] Generating custom wordlist...")
        subprocess.run([f'cewl -d 2 -m 5 -o -a -w {home_dir}/Wordlists/{args.domain}_custom.txt {target_url_string}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print("[-] Enumerating endpoints using custom wordlist...")
        subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/{args.domain}_custom.txt' -u {target_url_string}/FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '404 Not Found' -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
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

def crawl_scan(args, target_url_string):
    home_dir = get_home_dir()
    thisUrl = get_target_url_object(args, target_url_string)
    url_list = [f"{target_url_string}/"]
    link_list = []
    for endpoint in thisUrl['endpoints']:
        url_list.append(f"{target_url_string}/{endpoint['endpoint']}")
    for url in url_list:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.findAll('a')
        for link in links:
            href = link['href']
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
                            if '?' not in result_data['endpoint'] and '#' not in result_data['endpoint'] and p not in current_endpoints_list:
                                thisUrl['endpoints'].append(result_data)
            else:
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
                        if '?' not in result_data['endpoint'] and '#' not in result_data['endpoint'] and p not in current_endpoints_list:
                            thisUrl['endpoints'].append(result_data)
    write_wordlist(args, thisUrl)
    home_dir = get_home_dir()
    subprocess.run([f"{home_dir}/go/bin/ffuf -w '/tmp/crawl_wordlist_{args.domain}.txt' -u {target_url_string}/FUZZ -recursion -recursion-depth 4 -r -p 0.1-3.0 -sa -t 50 -fr '404 Not Found' -replay-proxy http://{args.proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
    thisUrl = get_target_url_object(args, target_url_string)
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
    # for endpoint in thisUrl['endpoints']:
        # if endpoint['endpoint'][0] == "/":
            # endpoint['endpoint'] = endpoint['endpoint'][1:]
    thisUrl['completedWordlists'].append("crawl")
    update_url(args, thisUrl)

def write_wordlist(args, thisUrl):
    f = open(f'/tmp/crawl_wordlist_{args.domain}.txt', 'w')
    for endpoint in thisUrl['endpoints']:
        f.write(f"{endpoint['endpoint']}\n")
    f.close()

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
    wordlist_arr = get_wordlists(args)
    wordlist_scan(args, wordlist_arr, target_url_string)
    cewl_scan(args, target_url_string)
    crawl_scan(args, target_url_string)
    print(f"[+] Ignite.py completed successfully!")

if __name__ == "__main__":
    args = arg_parse()
    main(args)