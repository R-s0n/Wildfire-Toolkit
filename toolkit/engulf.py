# Automated Parameter Discovery

import requests, sys, subprocess, getopt, json, time, math, random
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "u:"
long_options = ["url="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

hasUrl = False

for current_argument, current_value in arguments:
    if current_argument in ("-u", "--url"):
        url = current_value
        hasUrl = True

if hasUrl == False:
    print("[!] Please enter a URL using the -d or --domain flag...")
    sys.exit(2)

start = time.time()

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Engulf.py - Start Time: {now_start}\n")
f.close()

r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
thisUrl = r.json()

try:
    endpoints = thisUrl['endpoints']
    sorted_endpoints = sorted(endpoints, key=lambda k: k['statusCode'])
except:
    print(f"[!] URL '{url}' was not found in the database.  Exiting...")
    sys.exit(2)

counter = 0
for endpoint in sorted_endpoints:
    if str(endpoint['statusCode'])[0] == '2':
        counter += 1
print(f"[-] Starting parameter enumeration on {thisUrl['url']}")
print(f"[-] {counter} parameters found with a 2XX response code")

for endpoint in sorted_endpoints:
    if str(endpoint['statusCode'])[0] == '2':
        print(f"[-] Target Endpoint: {endpoint['endpoint']}\n[-] Status: {endpoint['statusCode']} -- Length: {endpoint['responseLength']}")
        try:
            thisEndpoint = endpoint['endpoint']
            if thisEndpoint[-4:] == ".ico" or thisEndpoint[-4:] == ".txt":
                print(f"[!] Endpoint is a static file.  Skipping...")
                continue
        except:
            print("[-] Targeting root directory...")
            thisEndpoint = "/"
        target = url + thisEndpoint
        print(f"[-] Scanning {target} for hidden parameters...")
        subprocess.run([f"arjun -u {target} -oJ /tmp/arjun-test.tmp -w /home/rs0n/Wordlists/SecLists/Discovery/Web-Content/params.txt -oB 10.0.0.208:8080 -q"], shell=True)
        with open('/tmp/arjun-test.tmp') as json_file:
            data = json.load(json_file)
        print(f"[+] Scan complete!")
        if target not in data:
            print(f"[!] No parameters found for {target} -- Skipping database update...")
            continue
        for param in data[target]['params']:
            print(f'[+] Parameter found: {param}')
        print(f"[-] Updating database...")
        try:
            r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
            updateUrl = r.json()
            for endpoint in updateUrl['endpoints']:
                if endpoint['endpoint'] == thisEndpoint:
                    endpointToUpdate = endpoint
                    endpointIndex = updateUrl['endpoints'].index(endpoint)
            updateUrl['endpoints'][endpointIndex]['arjun'] = {"method": data[target]['method'], "params": data[target]['params']}
            requests.post('http://10.0.0.211:8000/api/url/auto/update', json=updateUrl)
        except Exception as e:
            print(f"[!] Database updated failed.  ")
            print(f"[!] {e}")

print("[+] Parameter scanning using GET requests completed successfully!  Starting second scan using POST requests...")

for endpoint in sorted_endpoints:
    if str(endpoint['statusCode'])[0] == '2':
        print(f"[-] Target Endpoint: {endpoint['endpoint']}\n[-] Status: {endpoint['statusCode']} -- Length: {endpoint['responseLength']}")
        try:
            thisEndpoint = endpoint['endpoint']
            if thisEndpoint[-4:] == ".ico" or thisEndpoint[-4:] == ".txt":
                print(f"[!] Endpoint is a static file.  Skipping...")
                continue
        except:
            print("[-] Targeting root directory...")
            thisEndpoint = "/"
        target = url + thisEndpoint
        print(f"[-] Scanning {target} for hidden parameters...")
        subprocess.run([f"arjun -u {target} -oJ /tmp/arjun-test.tmp -w /home/rs0n/Wordlists/SecLists/Discovery/Web-Content/params.txt -oB 10.0.0.208:8080 -q -m POST"], shell=True)
        with open('/tmp/arjun-test.tmp') as json_file:
            data = json.load(json_file)
        print(f"[+] Scan complete!")
        if target not in data:
            print(f"[!] No parameters found for {target} -- Skipping database update...")
            continue
        for param in data[target]['params']:
            print(f'[+] Parameter found: {param}')
        print(f"[-] Updating database...")
        try:
            r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
            updateUrl = r.json()
            for endpoint in updateUrl['endpoints']:
                if endpoint['endpoint'] == thisEndpoint:
                    endpointToUpdate = endpoint
                    endpointIndex = updateUrl['endpoints'].index(endpoint)
            updateUrl['endpoints'][endpointIndex]['arjunPost'] = {"method": data[target]['method'], "params": data[target]['params']}
            requests.post('http://10.0.0.211:8000/api/url/auto/update', json=updateUrl)
        except Exception as e:
            print(f"[!] Database updated failed.  ")
            print(f"[!] {e}")

print("[+] Parameter scanning using POST requests completed successfully!  Starting final scan using POST requests in JSON format...")

for endpoint in sorted_endpoints:
    if str(endpoint['statusCode'])[0] == '2':
        print(f"[-] Target Endpoint: {endpoint['endpoint']}\n[-] Status: {endpoint['statusCode']} -- Length: {endpoint['responseLength']}")
        try:
            thisEndpoint = endpoint['endpoint']
            if thisEndpoint[-4:] == ".ico" or thisEndpoint[-4:] == ".txt":
                print(f"[!] Endpoint is a static file.  Skipping...")
                continue
        except:
            print("[-] Targeting root directory...")
            thisEndpoint = "/"
        target = url + thisEndpoint
        print(f"[-] Scanning {target} for hidden parameters...")
        subprocess.run([f"arjun -u {target} -oJ /tmp/arjun-test.tmp -w /home/rs0n/Wordlists/SecLists/Discovery/Web-Content/params.txt -oB 10.0.0.208:8080 -q -m JSON"], shell=True)
        with open('/tmp/arjun-test.tmp') as json_file:
            data = json.load(json_file)
        print(f"[+] Scan complete!")
        if target not in data:
            print(f"[!] No parameters found for {target} -- Skipping database update...")
            continue
        for param in data[target]['params']:
            print(f'[+] Parameter found: {param}')
        print(f"[-] Updating database...")
        try:
            r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
            updateUrl = r.json()
            for endpoint in updateUrl['endpoints']:
                if endpoint['endpoint'] == thisEndpoint:
                    endpointToUpdate = endpoint
                    endpointIndex = updateUrl['endpoints'].index(endpoint)
            updateUrl['endpoints'][endpointIndex]['arjunJson'] = {"method": data[target]['method'], "params": data[target]['params']}
            requests.post('http://10.0.0.211:8000/api/url/auto/update', json=updateUrl)
        except Exception as e:
            print(f"[!] Database updated failed.  ")
            print(f"[!] {e}")

end = time.time()
runtime_seconds = math.floor(end - start)
runtime_minutes = math.floor(runtime_seconds / 60)

print(f"[+] Engulf.py completed successfully in {runtime_minutes} minutes!")