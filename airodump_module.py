#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import pickle
import sys


with open('variables.pkl', 'rb') as f:
    selected_targets_number, target_bssid, target_essid, target_ch, card, token = pickle.load(f)


def rfkiller():
    check_kill = subprocess.Popen(['sudo airmon-ng check kill'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  shell=True)
    time.sleep(2)
    rf_kill = subprocess.Popen(['sudo rfkill unblock all'],
                               stdout=subprocess.PIPE,
                               shell=True)
    time.sleep(2)
    monitor_mode = subprocess.Popen(['sudo iw dev ' + str(card) + ' set type monitor'],
                                    stdout=subprocess.PIPE,
                                    shell=True)



def airodump_starter():
    global airodump_ng
    global timeout
    airodump_ng = subprocess.Popen(['sudo airodump-ng ' + str(card) + ' 2>&1 | grep -E "^.{30}" | grep -E "(([0-9A-Fa-f:]{17})\s+([0-9\-]+))"'],
                                   stdout=subprocess.PIPE,
                                   shell=True,
                                   preexec_fn=os.setsid)
    timeout = int(time.time()) + 5


while True:
    try:
        if airodump_ng.poll() is not None:
            rfkiller()
            airodump_starter()
    except:
        rfkiller()
        airodump_starter()
    if airodump_ng.poll() is None:
        output = airodump_ng.stdout.readline().decode('utf-8').strip()
        print(output)
        #sys.stdout.write(output)
        #sys.stdout.flush()
    if int(time.time()) > timeout:
        os.killpg(os.getpgid(airodump_ng.pid), signal.SIGTERM)
        rfkiller()
