import subprocess, argparse
from wildfire import Timer
from time import sleep

def tools_dir_check():
    home_dir = get_home_dir()
    go_check = subprocess.run([f"ls {home_dir}/Tools"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if go_check.returncode == 0:
        print("[+] Tools folder was found.")
        return True
    print("[!] Tools folder was NOT found.  Creating now...")
    return False

def create_tools_dir():
    home_dir = get_home_dir()
    subprocess.run([f"mkdir {home_dir}/Tools"], shell=True)
    install_check = subprocess.run([f"ls {home_dir}/Tools"], shell=True)
    if install_check.returncode == 0:
        print("[+] Tools directory successfully created.")
    else:
        print("[!] Tools directory was NOT successfully created!  Something is really jacked up.  Exiting...")
        exit()

def go_check():
    go_check = subprocess.run(["go version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if go_check.returncode == 0:
        print("[+] Go is already installed.")
        return True
    print("[!] Go is NOT already installed.  Installing now...")
    return False

def sublist3r_check():
    home_dir = get_home_dir()
    sublist3r_check = subprocess.run([f"python3 {home_dir}/Tools/Sublist3r/sublist3r.py --help"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if sublist3r_check.returncode == 0:
        print("[+] Sublist3r is already installed.")
        return True
    print("[!] Sublist3r is NOT already installed.  Installing now...")
    return False

def install_sublist3r():
    home_dir = get_home_dir()
    subprocess.run([f"cd {home_dir}/Tools; git clone https://github.com/aboul3la/Sublist3r.git"], shell=True)
    install_check = subprocess.run([f"python3 {home_dir}/Tools/Sublist3r/sublist3r.py --help"], shell=True)
    if install_check.returncode == 0:
        print("[+] Sublist3r installed successfully!")
    else:
        print("[!] Something went wrong!  Sublist3r was NOT installed successfully...")

def assetfinder_check():
    home_dir = get_home_dir()
    assetfinder_check = subprocess.run([f"{home_dir}/go/bin/assetfinder --help"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if assetfinder_check.returncode == 0:
        print("[+] Assetfinder is already installed.")
        return True
    print("[!] Assetfinder is NOT already installed.  Installing now...")
    return False

def install_assetfinder():
    home_dir = get_home_dir()
    subprocess.run([f"go install github.com/tomnomnom/assetfinder@latest"], shell=True)
    install_check = subprocess.run([f"{home_dir}/go/bin/assetfinder --help"], shell=True)
    if install_check.returncode == 0:
        print("[+] Assetfinder installed successfully!")
    else:
        print("[!] Something went wrong!  Assetfinder was NOT installed successfully...")

def gau_check():
    home_dir = get_home_dir()
    gau_check = subprocess.run([f"{home_dir}/go/bin/gau --help"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if gau_check.returncode == 0:
        print("[+] Gau is already installed.")
        return True
    print("[!] Gau is NOT already installed.  Installing now...")
    return False

def install_gau():
    home_dir = get_home_dir()
    subprocess.run([f"wget https://github.com/lc/gau/releases/download/v2.1.2/gau_2.1.2_linux_amd64.tar.gz;tar xvf gau_2.1.2_linux_amd64.tar.gz;mv gau {home_dir}/go/bin/gau;rm gau_2.1.2_linux_amd64.tar.gz"], shell=True)
    install_check = subprocess.run([f"{home_dir}/go/bin/gau --help"], shell=True)
    if install_check.returncode == 0:
        print("[+] Gau installed successfully!")
    else:
        print("[!] Something went wrong!  Gau was NOT installed successfully...")

def shosubgo_check():
    home_dir = get_home_dir()
    shosubgo_check = subprocess.run([f"ls {home_dir}/Tools/shosubgo/"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if shosubgo_check.returncode == 0:
        print("[+] Shosubgo is already installed.")
        return True
    print("[!] Shosubgo is NOT already installed.  Installing now...")
    return False

def install_shosubgo():
    home_dir = get_home_dir()
    subprocess.run([f"cd {home_dir}/Tools;git clone https://github.com/incogbyte/shosubgo.git"], shell=True)
    install_check = subprocess.run([f"ls {home_dir}/Tools/shosubgo/"], shell=True)
    if install_check.returncode == 0:
        print("[+] Shosubgo installed successfully!  Don't forget to add your API key in the .keystore file.")
    else:
        print("[!] Something went wrong!  Shosubgo was NOT installed successfully...")

def crt_check():
    home_dir = get_home_dir()
    crt_check = subprocess.run([f"ls {home_dir}/Tools/tlshelpers/"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if crt_check.returncode == 0:
        print("[+] TLSHelpers is already installed.")
        return True
    print("[!] TLSHelpers is NOT already installed.  Installing now...")
    return False

def install_crt():
    home_dir = get_home_dir()
    subprocess.run([f"cd {home_dir}/Tools;git clone https://github.com/hannob/tlshelpers.git"], shell=True)
    install_check = subprocess.run([f"ls {home_dir}/Tools/tlshelpers/"], shell=True)
    if install_check.returncode == 0:
        print("[+] TLSHelpers installed successfully!")
    else:
        print("[!] Something went wrong!  TLSHelpers was NOT installed successfully...")

def install_go():
    # To Update: https://golang.org/doc/install
    home_dir = get_home_dir()
    subprocess.run([f"sudo apt-get update && sudo apt-get install -y golang-go; sudo apt-get install -y gccgo-go; mkdir {home_dir}/go;"], shell=True)
    install_check = subprocess.run(["go version"], shell=True)
    if install_check.returncode == 0:
        print("[+] Go installed successfully!")
    else:
        print("[!] Something went wrong!  Go was NOT installed successfully...")

def get_home_dir():
    get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    return get_home_dir.stdout.replace("\n", "")

def keystore():
    home_dir = get_home_dir()
    keystore_check = subprocess.run([f"ls {home_dir}/.keys"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
    if keystore_check.returncode == 0:
        print("[+] Keys directory found.")
    else:
        print("[!] Keys directory NOT found!  Creating now...")
        subprocess.run([f"mkdir {home_dir}/.keys"], shell=True)
        keystore_check = subprocess.run([f"ls {home_dir}/.keys"], shell=True)
        if keystore_check.returncode == 0:
            print("[+] Keys directory created successfully!")
            subprocess.run([f"touch {home_dir}/.keys/slack_web_hook && touch {home_dir}/.keys/.keystore"], shell=True)

def arg_parse():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    return parser.parse_args()

def main(args):
    print("[+] Starting install script")
    print("[!] WARNING: The install.py script should not be run as sudo.  If you did, ctrl+c and re-run the script as a user.  I'll give you a couple seconds ;)")
    sleep(2)
    starter_timer = Timer()
    keystore()
    if tools_dir_check() is False:
        create_tools_dir()
    if go_check() is False:
        install_go()
    if sublist3r_check() is False:
        install_sublist3r()
    if assetfinder_check() is False:
        install_assetfinder()
    if gau_check() is False:
        install_gau()
    if crt_check() is False:
        install_crt()
    if shosubgo_check() is False:
        install_shosubgo()
    starter_timer.stop_timer()
    print(f"[+] Done!  Start: {starter_timer.get_start()}  |  Stop: {starter_timer.get_stop()}")

if __name__ == "__main__":
    args = arg_parse()
    main(args)
