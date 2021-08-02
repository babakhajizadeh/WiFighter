#!/usr/bin/env python3
import subprocess
import time
import requests
import json
import pickle


with open('variables.pkl', 'rb') as f:
    selected_targets_number, target_bssid, target_essid, target_ch, card, token = pickle.load(f)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def pushbullet_message(message):
    msg = {"type": "note", "title": "WiFi Attacker", "body": message}
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + token,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)



def recovery():
    network_service_restart = subprocess.Popen(['sudo service NetworkManager restart'],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT,
                                               shell=True,)
    rf_kill = subprocess.Popen(['sudo rfkill unblock all'],
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.PIPE,
                               shell=True)
    check_kill = subprocess.Popen(['sudo airmon-ng check kill'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  shell=True)
    time.sleep(10)
    monitor_mode = subprocess.Popen(['sudo iw dev ' + str(card) + ' set type monitor'],
                                    stdout=subprocess.PIPE,
                                    shell=True)


def internet():
    ping = subprocess.Popen(['ping www.google.com -c 2'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            shell=True)
    time.sleep(10)
    return_code = ping.poll()

    if return_code == 0:
        return True
    else:
        return False


print(" [i] Internet connection persistency control module started.")

while True:
    # uncomment for debug: print(internet())
    if not internet():
        print(f"{bcolors.WARNING} [!] Internet connection failed!.{bcolors.ENDC}")
        print(f"{bcolors.WARNING}     Attempting to recovery...{bcolors.ENDC}")
        recovery()
        while not internet():
            recovery()
        if internet():
            print(f"{bcolors.OKBLUE} [i] Internet connection has been recovered successfully{bcolors.ENDC}")
            print(f"{bcolors.OKBLUE}     No further actions is needed{bcolors.ENDC}")
