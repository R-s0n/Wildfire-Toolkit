import requests, sys, subprocess, getopt, json, time, math, random
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "d:u:P:s:p:t"
long_options = ["domain=","url=","proxy=","server=","port=","targeted"]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

hasFqdn = False
hasUrl = False
hasProxy = False
hasServer=  False
hasPort = False
targeted = False

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value
        hasFqdn = True
    if current_argument in ("-u", "--url"):
        url = current_value
        hasUrl = True
    if current_argument in ("-P", "--proxy"):
        proxy = current_value
        hasProxy = True
    if current_argument in ("-s", "--server"):
        server_ip = current_value
        hasServer = True
    if current_argument in ("-p", "--port"):
        server_port = current_value
        hasPort = True
    if current_argument in ("-t", "--targeted"):
        targeted = True

if hasFqdn == False or hasServer == False or hasPort == False:
    print("[!] USAGE: python3 ignite.py -d [TARGET_FQDN] -s [WAPT_FRAMEWORK_IP] -p [WAPT_FRAMEWORK_PORT] -P [BURP_SUITE_PROXY_IP]")
    sys.exit(2)


start = time.time()

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

try:
    now_start = datetime.now().strftime("%d-%m-%y_%I%p")
    f = open(f"{home_dir}/Logs/automation.log", "a")
    f.write(f"Ignite.py - Start Time: {now_start}\n")
    f.close()
    hasLog = True
except Exception as e:
    print("[!] No Log File Found.  Disabling Logging...")
    hasLog = False

r = requests.post(f'http://{server_ip}:{server_port}/api/auto', data={'fqdn':fqdn})
thisFqdn = r.json()

url_list = thisFqdn['targetUrls']

print(f"[-] Enumerating endpoints on {url_list[0]}")

for target_url in url_list:
    r = requests.post(f'http://{server_ip}:{server_port}/api/url/auto', data={'url':target_url})
    thisUrl = r.json()

if targeted:
    wordlist_arr = ["raft-large-directories.txt","raft-large-words.txt","api/api-endpoints.txt","api/api-seen-in-wild.txt","PHP.fuzz.txt","CMS/Django.txt","CMS/wp-plugins.fuzz.txt"]
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

if hasUrl == False:
    print("[-] No URL provided, pulling from database...")
    for target_url in url_list:
        l = len(wordlist_arr)-1
        wordlist_check = r = requests.post(f'http://{server_ip}:{server_port}/api/url/auto', data={'url':target_url})
        wordlist_check_data = wordlist_check.json()
        wordlist_len = len(wordlist_check_data['completedWordlists'])
        while wordlist_len < l:
            print(f"[*] {wordlist_len} out of {l} wordlists attempted...")
            r = requests.post(f'http://{server_ip}:{server_port}/api/url/auto', data={'url':target_url})
            thisUrl = r.json()
            print(thisUrl)
            wordlist = random.choice(wordlist_arr)
            print(thisUrl['completedWordlists'])
            if wordlist in thisUrl['completedWordlists']:
                print(f"[!] The {wordlist} wordlist has already been run against {target_url}!  Skipping...")
                i = wordlist_arr.index(wordlist)
                del wordlist_arr[i]
                continue
            thisUrl['completedWordlists'].append(wordlist)
            print(thisUrl['completedWordlists'])
            format_test = subprocess.run([f"head -n 1 '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
            print(format_test.stdout[0])
            if format_test.stdout[0] == "/":
                subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url}FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://{proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
            else:
                subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url}/FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://{proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
            i = wordlist_arr.index(wordlist)
            del wordlist_arr[i]
            with open('/tmp/ffuf-results.tmp') as json_file:
                data = json.load(json_file)
            for result in data['results']:
                result_data = {"endpoint":result['input']['FUZZ'], "statusCode":result['status'], "responseLength":result['length']}
                thisUrl['endpoints'].append(result_data)
            requests.post(f'http://{server_ip}:{server_port}/api/url/auto/update', json=thisUrl, headers={'Content-type':'application/json'})
            wordlist_len = len(thisUrl['completedWordlists'])
else:
    print(f"[-] Running scan on {url}...")
    target_url = url
    l = len(wordlist_arr)-1
    wordlist_check = r = requests.post(f'http://{server_ip}:{server_port}/api/url/auto', data={'url':target_url})
    wordlist_check_data = wordlist_check.json()
    wordlist_len = len(wordlist_check_data['completedWordlists'])
    while wordlist_len < l:
        print(f"[*] {wordlist_len} out of {l} wordlists attempted...")
        r = requests.post(f'http://{server_ip}:{server_port}/api/url/auto', data={'url':target_url})
        thisUrl = r.json()
        print(thisUrl)
        wordlist = random.choice(wordlist_arr)
        print(thisUrl['completedWordlists'])
        if wordlist in thisUrl['completedWordlists']:
            print(f"[!] The {wordlist} wordlist has already been run against {target_url}!  Skipping...")
            i = wordlist_arr.index(wordlist)
            del wordlist_arr[i]
            continue
        thisUrl['completedWordlists'].append(wordlist)
        print(thisUrl['completedWordlists'])
        format_test = subprocess.run([f"head -n 1 '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}'"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        print(format_test.stdout[0])
        if format_test.stdout[0] == "/":
            subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url}FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://{proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
        else:
            subprocess.run([f"{home_dir}/go/bin/ffuf -w '{home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}' -u {target_url}/FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://{proxy}:8080 -o /tmp/ffuf-results.tmp -of json"], shell=True)
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
            print(result_str)
            print(current_endpoints_list)
            if '?' not in result_data['endpoint'] and '#' not in result_data['endpoint'] and result_str not in current_endpoints_list:
                thisUrl['endpoints'].append(result_data)
        requests.post(f'http://{server_ip}:{server_port}/api/url/auto/update', json=thisUrl, headers={'Content-type':'application/json'})
        wordlist_len = len(thisUrl['completedWordlists'])

if hasLog == True:
    now_end = datetime.now().strftime("%d-%m-%y_%I%p")
    f = open(f"{home_dir}/Logs/automation.log", "a")
    f.write(f"Ignite.py - End Time: {now_end}\n")
    f.close()

end = time.time()
runtime_seconds = math.floor(end - start)
runtime_minutes = math.floor(runtime_seconds / 60)

print(f"[+] Ignite.py completed successfully in {runtime_minutes} minutes!")