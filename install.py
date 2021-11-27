import subprocess, argparse
from wildfire import Timer
from time import sleep

def go_install():
    home_dir = get_home_dir()
    print("[!] Go is NOT installed -- Installing now...")
    try:
        subprocess.run([f"sudo apt-get update && sudo apt-get install -y golang-go; sudo apt-get install -y gccgo-go; mkdir {home_dir}/go;"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print("[+] Go was successfully installed")
    except Exception as e:
        exception = str(e)
        print(f"[!] Something went wrong!  Exception:\n{exception}")

def go_check():
    go_check = subprocess.run(["go version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    if go_check.returncode == 0:
        return True
    return False

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

def arg_parse():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-S','--server', help='IP Address of MongoDB API', required=True)
    return parser.parse_args()

def main(args):
    starter_timer = Timer()
    go_check = subprocess.run(["go version"], shell=True)
    if go_check.returncode != 0:
        install_go()
    sleep(2)
    starter_timer.stop_timer()
    print(f"[+] Done!  Start: {starter_timer.get_start()}  |  Stop: {starter_timer.get_stop()}")

if __name__ == "__main__":
    args = arg_parse()
    main(args)