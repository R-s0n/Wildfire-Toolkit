import requests, sys, subprocess, getopt, json, time, math
from datetime import datetime

start = time.time()

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "hd:s:p:"
long_options = ["help","domain=","server=","port="]

help_notification = """
This tool is designed to automate the inital phase of my Recon methodology for Bug Bounty hunting.  
I have specifically designed this script around my workflow, but feel free to take the code and make 
it your own (I love Forks!).  Although I've configured the data structures and requests to work with 
my WAPT Framework, which uses a MongoDB database to store data through a Node/Express API, the code
could be easily refactored to work with a SQL or PostGRES database.  I'll work on a more universally
applicable version of this script as I get closer to releasing my WAPT Framework publically.  -rs0n

******************************************************************************************************
*              I AM NOT RESPONSABLE FOR HOW YOU USE THIS TOOL.  DON'T BE A DICK!                     *
******************************************************************************************************

                           (WARNING!  Do not run using sudo!)

           python3 fire_starter.py [-h --help] [-d --domain] [-s --server] [-p --port]
------------------------------------------------------------------------------------------------------
|  Short  |    Long    |  Required  |                               Notes                             |
|---------|------------|------------|-----------------------------------------------------------------|
|   -h    |  --help    |     no     |                   Display this help message                     |
|   -d    |  --org     |     yes    |                   Name of the root/seed FQDN                    |
|   -s    |  --server  |     yes    |           IP Address of the Node server hosting DB API          |
|   -p    |  --port    |     yes    |                Port of Node server hosting DB API               |
-------------------------------------------------------------------------------------------------------"""

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except Exception as e:
    print(f'[!] Exception: {e}')
    sys.exit(2)

hasDomain = False
hasServer = False
hasPort = False

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value
        hasDomain = True
    if current_argument in ("-s", "--server"):
        server_ip = current_value
        hasServer = True
    if current_argument in ("-p", "--port"):
        server_port = current_value
        hasPort = True
    if current_argument in ("-h", "--help"):
        print(help_notification)
        sys.exit(0)

if hasDomain is False or hasServer is False or hasPort is False:
    print(help_notification)
    sys.exit(2)

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Fire_starter.py - Start Time: {now_start}\n")
f.close()

r = requests.post(f'http://{server_ip}:{server_port}/api/auto', data={'fqdn':fqdn})
thisFqdn = r.json()

directory_check = subprocess.run([f"ls {home_dir}/Tools"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, shell=True)
if directory_check.returncode == 0:
    print("[+] Identified Tools directory")
else:
    print("[!] Could not locate Tools directory -- Creating now...")
    cloning = subprocess.run([f"mkdir {home_dir}/Tools"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Tools directory successfully created")

python3_check = subprocess.run(["python3 --version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if python3_check.returncode == 0:
    print("[+] Python3 is installed")
else :
    print("[!] Python3 is NOT installed -- Installing now...")
    cloning = subprocess.run(["sudo apt-get install -y python3"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Python3 was successfully installed")


pip3_check = subprocess.run(["pip3 --version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if pip3_check.returncode == 0:
    print("[+] Pip3 is installed")
else :
    print("[!] Pip3 is NOT installed -- Installing now...")
    cloning = subprocess.run(["sudo apt-get install -y python3-pip"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Pip3 was successfully installed")

go_check = subprocess.run(["go version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if go_check.returncode == 0:
    print("[+] Go is installed")
else :
    print("[!] Go is NOT installed -- Installing now...")
    cloning = subprocess.run(["sudo apt-get install -y golang-go; apt-get install -y gccgo-go; mkdir {home_dir}/go;"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Go was successfully installed")

print("[-] Starting Subdomain Scraping Modules...")

# Subdomain Enumeration
## Subdomain Scraping
### Sublist3r

try:
    sublist3r_check = subprocess.run([f"ls {home_dir}/Tools/Sublist3r"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if sublist3r_check.returncode == 0:
        print(f"[+] Sublist3r found in {home_dir}/Tools directory")
    else :
        print(f"[!] Sublist3r NOT found in {home_dir}/Tools directory -- Installing now...")
        cloning = subprocess.run([f"cd {home_dir}/Tools; sudo git clone https://github.com/aboul3la/Sublist3r.git"], stdout=subprocess.DEVNULL, shell=True)
        print(f"[+] Sublist3r found in {home_dir}/Tools directory -- Installing dependencies...")
        install = subprocess.run([f"sudo pip3 install -r {home_dir}/Tools/Sublist3r/requirements.txt"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Sublist3r successfully installed!")
    print(f"[-] Running Sublist3r against {fqdn}...")
    sublist3r_results = subprocess.run([f"python3 {home_dir}/Tools/Sublist3r/sublist3r.py -d {fqdn} -t 50 -o /tmp/sublist3r.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open("/tmp/sublist3r.tmp", "r")
    sublist3r_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm /tmp/sublist3r.tmp"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Sublist3r completed successfully!")
    thisFqdn['recon']['subdomains']['sublist3r'] = sublist3r_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Sublist3r module did NOT complete successfully -- skipping...")

### Amass

try:
    amass_check = subprocess.run(["amass -h"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if amass_check.returncode == 0:
        print("[+] Amass is already installed")
    else :
        print("[!] Amass is NOT already installed -- Installing now...")
        cloning = subprocess.run(["sudo apt-get install amass"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Amass successfully installed!")
    print(f"[-] Running Amass against {fqdn}...")
    regex = "{1,3}"
    amass_results = subprocess.run([f"amass enum -src -ip -brute -min-for-recursive 2 -d {fqdn} -o /tmp/amass.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    subprocess.run([f"cp /tmp/amass.tmp /tmp/amass.full.tmp"], stdout=subprocess.DEVNULL, shell=True)
    subprocess.run([f"sed -i -E 's/\[(.*?)\] +//g' /tmp/amass.tmp"], stdout=subprocess.DEVNULL, shell=True)
    subprocess.run([f"sed -i -E 's/ ([0-9]{regex}\.)[0-9].*//g' /tmp/amass.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    amass_file = open(f"/tmp/amass.tmp", 'r')
    amass_file_lines = amass_file.readlines()
    amass_file.close()
    new_lines = []
    for line in amass_file_lines:
        if " " in line:
            subdomain = line.split(" ")[0] + "\n"
            new_lines.append(subdomain)
        else:
            new_lines.append(line)
    subprocess.run(["rm -rf /tmp/amass.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    amass_file = open(f"/tmp/amass.tmp", 'w')
    amass_file.writelines(new_lines)
    amass_file.close()
    f = open(f"/tmp/amass.tmp", "r")
    amass_arr = f.read().rstrip().split("\n")
    f.close()
    print("[+] Amass completed successfully!")
    thisFqdn['recon']['subdomains']['amass'] = amass_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Amass module did NOT complete successfully -- skipping...")

### Assetfinder

try:
    assetfinder_check = subprocess.run([f"{home_dir}/go/bin/assetfinder -h"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if assetfinder_check.returncode == 0:
        print("[+] Assetfinder is already installed")
    else :
        print("[!] Assetfinder is NOT already installed -- Installing now...")
        cloning = subprocess.run(["go get -u github.com/tomnomnom/assetfinder"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Assetfinder successfully installed!")
    print(f"[-] Running Assetfinder against {fqdn}...")
    assetfinder_results = subprocess.run([f"{home_dir}/go/bin/assetfinder --subs-only {fqdn} > /tmp/assetfinder.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/assetfinder.tmp", "r")
    assetfinder_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm /tmp/assetfinder.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] Assetfinder completed successfully!")
    thisFqdn['recon']['subdomains']['assetfinder'] = assetfinder_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Assetfinder module did NOT complete successfully -- skipping...")

### GetAllUrls (GAU)

try:
    gau_check = subprocess.run([f"{home_dir}/go/bin/gau -h"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if gau_check.returncode == 0:
        print("[+] Gau is already installed")
    else :
        print("[!] Gau is NOT already installed -- Installing now...")
        cloning = subprocess.run(["GO111MODULE=on go get -u -v github.com/lc/gau"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Gau successfully installed!")
    print(f"[-] Running Gau against {fqdn}...")
    gau_results = subprocess.run([f"{home_dir}/go/bin/gau -subs {fqdn} | cut -d / -f 3 | sort -u > /tmp/gau.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/gau.tmp", "r")
    gau_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm /tmp/gau.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] Gau completed successfully!")
    thisFqdn['recon']['subdomains']['gau'] = gau_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Gau module did NOT complete successfully -- skipping...")

### Certificate Transparency Logs

try:
    ctl_check = subprocess.run([f"ls {home_dir}/Tools/tlshelpers"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if ctl_check.returncode == 0:
        print("[+] Crt.sh is already installed")
    else :
        print("[!] Crt.sh is NOT already installed -- Installing now...")
        cloning = subprocess.run([f"cd {home_dir}/Tools; sudo git clone https://github.com/hannob/tlshelpers.git"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Crt.sh successfully installed!")
    print(f"[-] Running Crt.sh against {fqdn}...")
    ctl_results = subprocess.run([f"cd {home_dir}/Tools/tlshelpers; ./getsubdomain {fqdn} > /tmp/ctl.tmp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/ctl.tmp", "r")
    ctl_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm /tmp/ctl.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] Crt.sh completed successfully!")
    thisFqdn['recon']['subdomains']['ctl'] = ctl_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Sublist3r module did NOT complete successfully -- skipping...")

### Shosubgo

try:
    shosubgo_check = subprocess.run([f"ls {home_dir}/Tools/shosubgo"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if shosubgo_check.returncode == 0:
        print(f"[+] Shosubgo found in {home_dir}/Tools directory")
    else :
        print(f"[!] Shosubgo NOT found in {home_dir}/Tools directory -- Installing now...")
        cloning = subprocess.run([f"cd {home_dir}/Tools; git clone https://github.com/pownx/shosubgo.git"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Shosubgo successfully installed!")
    print(f"[-] Running Shosubgo against {fqdn}...")
    f = open(f"{home_dir}/.keys/.keystore", "r")
    tempArr = f.read().split("\n")
    for line in tempArr:
        temp = line.split(":")
        if temp[0] == "shodan":
            key = temp[1]
    shosubgo_results = subprocess.run([f"go run {home_dir}/Tools/shosubgo/main.go -d {fqdn} -s {key}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    shosubgo_arr = shosubgo_results.stdout.rstrip().split("\n")
    print("[+] Shosubgo completed successfully!")
    thisFqdn['recon']['subdomains']['shosubgo'] = shosubgo_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Shosubgo module did NOT complete successfully -- skipping...")

### Subfinder

try:
    subfinder_check = subprocess.run([f"ls {home_dir}/go/bin/subfinder"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if subfinder_check.returncode == 0:
        print("[+] Subfinder is already installed")
    else :
        print("[!] Subfinder is NOT already installed -- Installing now...")
        cloning = subprocess.run(["GO111MODULE=on go get -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Subfinder successfully installed!")
        print(f"[+] NOTE: Adding API Keys to {home_dir}/.config/subfinder/config.yaml will dramatically increase subfinder's ability to discover subdomains")
    print(f"[-] Running Subfinder against {fqdn}...")
    subfinder_results = subprocess.run([f'{home_dir}/go/bin/subfinder -d {fqdn} -o /tmp/subfinder.tmp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/subfinder.tmp", "r")
    subfinder_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm -rf /tmp/subfinder.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] Subfinder completed successfully!")
    thisFqdn['recon']['subdomains']['subfinder'] = subfinder_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Subfinder module did NOT complete successfully -- skipping...")

### Github-Subdomains

try:
    github_search_check = subprocess.run([f"ls {home_dir}/Tools/github-search"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if github_search_check.returncode == 0:
        print(f"[+] Github-Search found in {home_dir}/Tools directory")
    else :
        print(f"[!] Github-Search NOT found in {home_dir}/Tools directory -- Installing now...")
        cloning = subprocess.run([f"cd {home_dir}/Tools; git clone https://github.com/gwen001/github-search.git; cd github-search; pip3 install -r requirements2.txt"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Github-Search successfully installed!")
    f = open(f"{home_dir}/.keys/.keystore", "r")
    tempArr = f.read().split("\n")
    for line in tempArr:
        temp = line.split(":")
        if temp[0] == "github":
            key = temp[1]
    github_search_iteration_arr = []
    for x in range(5):
        i = x + 1
        print(f"[-] Running Github-Search against {fqdn} -- Iteration {i} of 5...")
        github_search_results = subprocess.run([f"python3 {home_dir}/Tools/github-search/github-subdomains.py -d {fqdn} -t {key}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        github_search_arr = github_search_results.stdout.rstrip().split("\n")
        for link in github_search_arr:
            if link not in github_search_iteration_arr:
                github_search_iteration_arr.append(link)
        print(f"[-] Iteration {i} complete!")
    print("[+] Github-Search completed successfully!")
    thisFqdn['recon']['subdomains']['githubSearch'] = github_search_iteration_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Github-Search module did NOT complete successfully -- skipping...")

print("[+] Subdomain Scraping Modules Completed!")
print("[-] Starting Link / JS Discovery Modules...")

### GoSpider

try:
    gospider_check = subprocess.run([f"ls {home_dir}/go/bin/gospider"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if gospider_check.returncode == 0:
        print("[+] Gospider is already installed")
    else :
        print("[!] Gospider is NOT already installed -- Installing now...")
        cloning = subprocess.run(["go get -u github.com/jaeles-project/gospider"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] Gospider successfully installed!")
    print(f"[-] Running Gospider against {fqdn}...")
    gospider_results = subprocess.run([f'cd {home_dir}/go/bin;  ./gospider -s "https://{fqdn}" -o /tmp/gospider -c 10 -d 1 --other-source --include-subs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    outputFile = fqdn.replace(".", "_")
    f = open(f"/tmp/gospider/{outputFile}", "r")
    gospider_arr = f.read().rstrip().split("\n")
    gospider_link_arr = []
    for line in gospider_arr:
        new_arr = line.split(" ")
        if len(new_arr) > 2:
            temp_arr = new_arr[2].split("/")
            if len(temp_arr) > 2:
                if temp_arr[2] not in gospider_link_arr:
                    gospider_link_arr.append(temp_arr[2])
    f.close()
    subprocess.run(["rm -rf /tmp/gospider"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] Gospider completed successfully!")
    thisFqdn['recon']['subdomains']['gospider'] = gospider_link_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Gospider module did NOT complete successfully -- skipping...")

# ### Hakrawler
# 
# try:
#     hakrawler = subprocess.run([f"ls {home_dir}/go/bin/hakrawler"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
#     if hakrawler.returncode == 0:
#         print("[+] Hakrawler is already installed")
#     else :
#         print("[!] Hakrawler is NOT already installed -- Installing now...")
#         cloning = subprocess.run(["go get github.com/hakluke/hakrawler"], stdout=subprocess.DEVNULL, shell=True)
#         print("[+] Hakrawler successfully installed!")
#     print(f"[-] Running Hakrawler against {fqdn}...")
#     # Add after debug: stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
#     subprocess.run([f'cd {home_dir}/go/bin; cat /tmp/amass.tmp | ./hakrawler -subs -d 3 -u > /tmp/hakrawler.tmp'], shell=True)
#     f = open(f"/tmp/hakrawler.tmp", "r")
#     hakrawler_arr = f.read().rstrip().split("\n")
#     hakrawler_link_arr = []
#     for line in hakrawler_arr:
#         new_arr = line.split(" ")
#         if len(new_arr) > 1:
#             temp_arr = new_arr[1].split("/")
#             if len(temp_arr) > 2:
#                 if temp_arr[2] not in hakrawler_link_arr:
#                     hakrawler_link_arr.append(temp_arr[2])
#     f.close()
#     subprocess.run(["rm -rf /tmp/hakrawler"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
#     print("[+] Hakwraler completed successfully!")
#     thisFqdn['recon']['subdomains']['hakrawler'] = hakrawler_link_arr
# except Exception as e:
#     print(f'[!] Exception: {e}')
#     print("[!] Hakrawler module did NOT complete successfully -- skipping...")

### SubDomainizer

try:
    subdomainizer_check = subprocess.run([f"ls {home_dir}/Tools/SubDomainizer"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if subdomainizer_check.returncode == 0:
        print(f"[+] SubDomainizer found in {home_dir}/Tools directory")
    else :
        print(f"[!] SubDomainizer NOT found in {home_dir}/Tools directory -- Installing now...")
        cloning = subprocess.run([f"cd {home_dir}/Tools; git clone https://github.com/nsonaniya2010/SubDomainizer.git"], stdout=subprocess.DEVNULL, shell=True)
        print(f"[+] SubDomainizer found in {home_dir}/Tools directory -- Installing dependencies...")
        install = subprocess.run([f"sudo pip3 install -r {home_dir}/Tools/SubDomainizer/requirements.txt"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] SubDomainizer successfully installed!")
    print(f"[-] Running SubDomainizer against {fqdn}...")
    subdomainizer_results = subprocess.run([f"python3 {home_dir}/Tools/SubDomainizer/SubDomainizer.py -l /tmp/amass.tmp -o /tmp/subdomainizer.tmp"], stdout=subprocess.PIPE, text=True, shell=True)
    f = open("/tmp/subdomainizer.tmp", "r")
    subdomainizer_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm /tmp/subdomainizer.tmp"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] SubDomainizer completed successfully!")
    thisFqdn['recon']['subdomains']['subdomainizer'] = subdomainizer_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] SubDomainizer module did NOT complete successfully -- skipping...")

print("[+] Link / JS Discovery Modules Completed!")
print("[-] Starting Subdomain Bruteforcing Modules...")

directory_check = subprocess.run([f"ls {home_dir}/Wordlists"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if directory_check.returncode == 0:
    print("[+] Identified Wordlists directory")
else:
    print("[!] Could not locate Wordlists directory -- Creating now...")
    cloning = subprocess.run([f"mkdir {home_dir}/Wordlists"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Wordlists directory successfully created")


wordlist_check = subprocess.run([f"ls {home_dir}/Wordlists/all.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if wordlist_check.returncode == 0:
    print("[+] Identified all.txt wordlist (Shoutout to JHaddix!)")
else:
    print("[!] Could not identify all.txt wordlist -- Downloading now...")
    cloning = subprocess.run([f"cd {home_dir}/Wordlists; wget https://gist.githubusercontent.com/jhaddix/86a06c5dc309d08580a018c66354a056/raw/96f4e51d96b2203f19f6381c8c545b278eaa0837/all.txt"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] All.txt wordlist downloaded successfully!")

resolvers_check = subprocess.run([f"ls {home_dir}/Wordlists/resolvers.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
if resolvers_check.returncode == 0:
    print("[+] Identified resolvers.txt wordlist")
else:
    print("[!] Could not identify resolvers.txt wordlist -- Downloading now...")
    cloning = subprocess.run([f"cd {home_dir}/Wordlists; wget https://raw.githubusercontent.com/janmasarik/resolvers/master/resolvers.txt"], stdout=subprocess.DEVNULL, shell=True)
    print("[+] Resolvers.txt wordlist downloaded successfully!")

### ShuffleDNS

try:
    shuffledns_check = subprocess.run([f"ls {home_dir}/go/bin/shuffledns"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if shuffledns_check.returncode == 0:
        print("[+] ShuffleDNS is already installed")
    else :
        print("[!] ShuffleDNS is NOT already installed -- Installing now...")
        cloning = subprocess.run(["sudo apt-get install -y massdns; GO111MODULE=on go get -v github.com/projectdiscovery/shuffledns/cmd/shuffledns"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] ShuffleDNS successfully installed!")
    print(f"[-] Running ShuffleDNS against {fqdn} using massive wordlist...")
    shuffledns_results = subprocess.run([f'{home_dir}/go/bin/shuffledns -d {fqdn} -w {home_dir}/Wordlists/all.txt -r {home_dir}/Wordlists/resolvers.txt -o /tmp/shuffledns.tmp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/shuffledns.tmp", "r")
    shuffledns_arr = f.read().rstrip().split("\n")
    for subdomain in shuffledns_arr:
        if fqdn not in subdomain:
            i = shuffledns_arr.index(subdomain)
            del shuffledns_arr[i]
    f.close()
    subprocess.run(["rm -rf /tmp/shuffledns.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] ShuffleDNS completed successfully!")
    thisFqdn['recon']['subdomains']['shuffledns'] = shuffledns_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] ShuffleDNS module did NOT complete successfully -- skipping...")

### Build Custom Wordlist

try:
    cewl_check = subprocess.run([f"cewl -h"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if shuffledns_check.returncode == 0:
        print("[+] CeWL is already installed")
    else :
        print("[!] CeWL is NOT already installed -- Installing now...")
        subprocess.run(["sudo apt-get install -y cewl"], stdout=subprocess.DEVNULL, shell=True)
        print("[+] CeWL successfully installed!")
    print(f"[-] Running CeWL against {fqdn} to build a custom wordlist...")
    cewl_results = subprocess.run([f'cewl -d 2 -m 5 -o -a -w {home_dir}/Wordlists/{fqdn}_custom.txt https://{fqdn}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    wordlist = cewl_results.stdout.split("\n")
    print("[+] Custom wordlist built successfully!")
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] Custom wordlist module did NOT complete successfully -- skipping...")

### ShuffleDNS Custom

try:
    print(f"[-] Running ShuffleDNS against {fqdn} using custom wordlist...")
    shuffledns_results = subprocess.run([f'{home_dir}/go/bin/shuffledns -d {fqdn} -w {home_dir}/Wordlists/{fqdn}_custom.txt -r {home_dir}/Wordlists/resolvers.txt -o /tmp/shuffledns_custom.tmp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    f = open(f"/tmp/shuffledns_custom.tmp", "r")
    shuffledns_custom_arr = f.read().rstrip().split("\n")
    f.close()
    subprocess.run(["rm -rf /tmp/shuffledns_custom.tmp"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    print("[+] ShuffleDNS completed successfully!")
    thisFqdn['recon']['subdomains']['shufflednsCustom'] = shuffledns_custom_arr
except Exception as e:
    print(f'[!] Exception: {e}')
    print("[!] ShuffleDNS module did NOT complete successfully -- skipping...")

print("[+] Subdomain Bruteforcing Modules completed successfully!")

print("[-] Building consolidated list...")

# Final Analysis
## Build Consolidated List

consolidated = thisFqdn['recon']['subdomains']['consolidated']
consolidatedNew = []
for key in thisFqdn['recon']['subdomains']:
    for subdomain in thisFqdn['recon']['subdomains'][key]:
        if subdomain not in consolidated and fqdn in subdomain and "?" not in subdomain:
            consolidated.append(subdomain)
            consolidatedNew.append(subdomain)
thisFqdn['recon']['subdomains']['consolidated'] = consolidated
thisFqdn['recon']['subdomains']['consolidatedNew'] = consolidatedNew

temp = []
for subdomain in thisFqdn['recon']['subdomains']['consolidated']:
    if "?" not in subdomain:
        temp.append(subdomain)
thisFqdn['recon']['subdomains']['consolidated'] = temp

temp = []
for subdomain in thisFqdn['recon']['subdomains']['consolidatedNew']:
    if "?" not in subdomain:
        temp.append(subdomain)
thisFqdn['recon']['subdomains']['consolidatedNew'] = temp

print("[-] Updating database...")

# Send new fqdn object
r = requests.post(f'http://{server_ip}:{server_port}/api/auto/update', json=thisFqdn, headers={'Content-type':'application/json'})

end = time.time()
runtime_seconds = math.floor(end - start)
runtime_minutes = math.floor(runtime_seconds / 60)
new_subdomain_length = len(consolidatedNew)

message_json = {'text':f'The subdomain list for {fqdn} has been updated with {new_subdomain_length} new subdomains!  Scantime: {runtime_minutes} minutes','username':'Recon Box','icon_emoji':':eyes:'}
f = open(f'{home_dir}/.keys/slack_web_hook')
token = f.read()
slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)

now_end = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Fire_starter.py - End Time: {now_end}\n")
f.close()

print(f"[+] Fire_Starter completed successfully in {runtime_minutes} minutes!")