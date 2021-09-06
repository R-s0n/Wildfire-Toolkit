import requests, argparse, subprocess, sys, json, math, threading
from bs4 import BeautifulSoup
from time import sleep
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

script_links = []
raw_scripts = []
links = []
extension_blacklist = [".pdf", ".jpg", ".png", ".svg"]

def get_links(fqdn, url):
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    a_tags = soup.find_all('a')
    for tag in a_tags:
        if tag.get('href') != None:
            tag_to_add = tag.get('href')
            if ".pdf" in tag_to_add or ".jpg" in tag_to_add or ".png" in tag_to_add or ".svg" in tag_to_add or "mailto:" in tag_to_add:
                continue
            if "?" in tag_to_add:
                tag_to_add = tag_to_add.split("?")[0]
            if "#" in tag_to_add:
                tag_to_add = tag_to_add.split("#")[0]
            if tag_to_add[:4] == "http":
                if tag_to_add[:len(url)] == url:
                    if tag_to_add not in links:
                        links.append(tag_to_add)
            elif tag_to_add[:1] == "/":
                tag_to_add = f"{fqdn}{tag_to_add}"
                if tag_to_add not in links:
                    links.append(tag_to_add)
            else:
                tag_to_add = f"{fqdn}/{tag_to_add}"
                if tag_to_add not in links:
                    links.append(tag_to_add)

def get_scripts(url):
    res = requests.get(url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    script_tags = soup.find_all('script')
    for tag in script_tags:
        if tag.get('src') != None:
            tag_to_add = tag.get('src')
            if "?" in tag_to_add:
                tag_to_add = tag_to_add.split("?")[0]
            if tag_to_add[:4] == "http":
                if tag_to_add not in script_links:
                    script_links.append(tag_to_add)
            elif tag_to_add[:1] == "/":
                tag_to_add = f"{url}{tag_to_add}"
                if tag_to_add not in script_links:
                    script_links.append(f"{url}{tag_to_add}")
            else:
                tag_to_add = f"{url}/{tag_to_add}"
                if tag_to_add not in script_links:
                    script_links.append(f"{url}/{tag_to_add}")

def crawl_links(fqdn, depth):
    if depth == "full":
        while True:
            num_of_links = len(links)
            temp = links
            for link in temp:
                if ".pdf" in link or ".jpg" in link or ".png" in link or ".svg" in link or "mailto:" in link:
                    links.remove(link)
                    continue
                else:
                    get_links(fqdn, link)
            if len(links) == num_of_links:
                return len(links)
    else:
        counter = 1
        while True:
            num_of_links = len(links)
            temp = links
            for link in temp:
                if ".pdf" in link or ".jpg" in link or ".png" in link or ".svg" in link or "mailto:" in link:
                    links.remove(link)
                    continue
                else:
                    get_links(fqdn, link)
            if len(links) == num_of_links or counter >= int(depth):
                return len(links)
            counter += 1

def clean_urls(fqdn_list):
    clean_url_list = []
    for fqdn in fqdn_list:
        for url in fqdn:
            if "?" in url:
                url_split = url.split("?")
                if url_split[0] not in clean_url_list:
                    clean_url_list.append(url_split[0])
            else:
                if url not in clean_url_list:
                    clean_url_list.append(url)
    return clean_url_list

def get_home_dir():
    get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return get_home_dir.stdout.replace("\n", "")

def send_slack_notification(args, url):
    home_dir = get_home_dir()
    message_json = {'text':f'Package {args.package} was found running on {url}!  (This will have a lot more information after I add this to the framework...)','username':'Vuln Disco Box','icon_emoji':':dart:'}
    f = open(f'{home_dir}/.keys/slack_web_hook')
    token = f.read()
    slack_auto = requests.post(f'https://hooks.slack.com/services/{token}', json=message_json)

def wappalyzer(url):
    wappalyzer = subprocess.run([f'wappalyzer {url} -p'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return wappalyzer.stdout

def npm_package_scan(self, args, url):
    if "http" in url:
        print(f"[-] Scanning {url}...")
        get_links(url, url)
        # Uncomment to add crawling
        # link_number = crawl_links(url, "1")
        wappalyzer_string = wappalyzer(url)
        wappalyzer_json = json.loads(wappalyzer_string)
        if args.package in wappalyzer_string:
            print(f"[+] Package {args.package} was found on {url}! (From Wappalyzer)")
            send_slack_notification(args, url)
            print(json.dumps(wappalyzer_json, indent=4))
        for link in links:
            get_scripts(link)
        for script in script_links:
            if args.package.lower() in script.lower():
                print(f"[+] Package {args.package} was found on {url}! (From Script Scan)")
                send_slack_notification(args, url)
                print(json.dumps(wappalyzer_json, indent=4))


def get_fqdns(args):
    res = requests.post(f'http://{args.server}:{args.port}/api/fqdn/all')
    fqdn_json = res.json()
    fqdn_list = []
    for fqdn in fqdn_json:
        fqdn_list.append(fqdn['recon']['subdomains']['httprobe'])
    return fqdn_list


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    parser.add_argument('-P','--port', help='Port of MongoDB API', required=True)
    parser.add_argument('-T','--threads', help='Number of Threads', required=True)
    parser.add_argument('-j','--js', help='Scan For JavaScript Package', required=False, action='store_true')
    parser.add_argument('-p','--package', help='Name of JavaScript Package', required=False)
    return parser.parse_args()

def main(args):
    if args.js is False:
        print("[!] Please select atleast one scanning type ( -j/--js | )")
        sys.exit(2)
    if args.js is True and not args.package:
        print("[!] Please include the name of the JavaScript package to scan for (-p/--package)")
        sys.exit(2)
    fqdn_list = get_fqdns(args)
    clean_url_list = clean_urls(fqdn_list)
    while len(clean_url_list) > 0:
        if len(clean_url_list) < int(args.threads):
            x_ls = list(range(len(clean_url_list)))
        else:
            x_ls = list(range(int(args.threads)))
        thread_list = []
        for x in x_ls:
            u = clean_url_list[0]
            thisUrl = clean_url_list[0]
            clean_url_list.remove(u)
            thread = threading.Thread(target=npm_package_scan, args=(x, args, u))
            thread_list.append(thread)
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        new_length = len(clean_url_list)
        print(f"URLs remaining: {new_length}")
    npm_package_scan(args, clean_url_list)
    print("[+] Done!")

if __name__ == "__main__":
    args = arg_parse()
    main(args)