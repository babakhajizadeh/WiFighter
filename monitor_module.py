#!/usr/bin/env python3
import subprocess
import time
import requests
import json
import pickle



with open('variables.pkl', 'rb') as f:
    selected_targets_number, target_bssid, target_essid, target_ch, card, token = pickle.load(f)

airodump_module = subprocess.Popen(['sudo ./airodump_module.py'],
                               stdout=subprocess.PIPE,
                               shell=True)

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


print(f"{bcolors.WARNING} [!] Air monitoring of selected target(s) started!{bcolors.ENDC}", flush=True)
pushbullet_message("Air monitoring of selected target(s) started!")


target0 = selected_targets_number[0]
try:
    target1 = selected_targets_number[1]
    double_target = True
except IndexError:
    double_target = False
target0_message_exception_OPN = False
target0_message_exception_TurnedOFF = False
target1_message_exception_OPN = False
target1_message_exception_TurnedOFF = False
while True:
    print("looped once")
    time.sleep(1)
    output = airodump_module.stdout.readline().strip()
    print(output,flush=True)
    if str(target_bssid[target0]) in output:
        if "WPA" in output or "WEP" in output:
            # reseting the being visible on air time out
            timeout = int(time.time()) + 6
        if "OPN" in output:
            if not target0_message_exception_OPN:
                pushbullet_message("A target's password reset!")
                pushbullet_message("A target's password reset!")
                target0_message_exception_OPN = True
                print(f"{bcolors.WARNING} [!] TARGET !{bcolors.ENDC}", target_essid[target0],
                      f"{bcolors.WARNING} PASSWORD HAS BEEN RESET!!!{bcolors.ENDC}", flush=True)
    if time.time() > timeout:
        if not target0_message_exception_TurnedOFF:
            target0_message_exception_TurnedOFF = True
            pushbullet_message("A Target has gone offline! Stay on touch!")
            print(f"{bcolors.WARNING} [!] Target !{bcolors.ENDC}", target_essid[target0],
                  f"{bcolors.WARNING} might have gone offline! Stay careful!{bcolors.ENDC}", flush=True)


    if double_target:
        if str(target_bssid[target1]) in output:
            if "WPA" in output or "WEP" in output:
                # reseting the being visible on air time out
                timeout = int(time.time()) + 6
            if "OPN" in output:
                if not target1_message_exception_OPN:
                    pushbullet_message("A target's password reset!")
                    pushbullet_message("A target's password reset!")
                    target1_message_exception_OPN = True
                print(f"{bcolors.WARNING} [1] TARGET !{bcolors.ENDC}", target_essid[target1],
                      f"{bcolors.WARNING} PASSWORD HAS BEEN RESET!!!{bcolors.ENDC}", flush=True)
        if time.time() > timeout:
            if not target1_message_exception_TurnedOFF:
                target1_message_exception_TurnedOFF = True
                pushbullet_message("A Target has gone offline! Stay on touch!")
                print(f"{bcolors.WARNING} [1] Target !{bcolors.ENDC}", target_essid[target1],
                      f"{bcolors.WARNING} might have gone offline! Stay careful!{bcolors.ENDC}", flush=True)

