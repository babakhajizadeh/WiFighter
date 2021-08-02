#!/usr/bin/env python3
# coded by Leukosyte
# https://www.instagram.com/leukosyte.social/

import os
import sys
import platform
import subprocess
import banner
import time
import requests
import json
import signal
import pickle

from random import randint

target_bssid = []
target_pwr = []
target_ch = []
target_essid = []
card = ""
token = ""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class target_reader:
    def __init__(self, output):
        def pwrgraphic(out):
            if out <= 50:
                return "[⚪⚪⚪⚪⚪]"
            if 50 < out < 60:
                return "[⚪⚪⚪⚪⚫]"
            if 60 < out < 70:
                return "[⚪⚪⚪⚫⚫]"
            if 70 < out < 80:
                return "[⚪⚪⚫⚫⚫]"
            if out > 80:
                return "[⚪⚫⚫⚫⚫]"
        self.fullline = output
        self.bssid = output[1:18]
        self.pwr = pwrgraphic(int(output[21:23]))
        self.ch = output[47:50].strip()
        self.essid = (output[75:93]).strip()


def selector(total_target_number):
    selected_targets_number = list(map(int, input("     Inputs:").split()))
    try:
        while (selected_targets_number[0] not in range(0,total_target_number)) or (selected_targets_number[1] not in range(0,total_target_number)) :
            print(f"{bcolors.WARNING} [!] Selected target(s) out of range!, Please try again.{bcolors.ENDC}")
            selected_targets_number = list(map(int, input("     Inputs:").split()))
    except IndexError:
        if selected_targets_number[0] not in range(0,total_target_number):
            return selected_targets_number
    return selected_targets_number


def pushbullet_message(message):
    global token
    msg = {"type": "note", "title": "WiFi Attacker", "body": message}
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + token,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)


def instructions():
    print(" section is under construction")


def main():
    if os.geteuid() != 0:
        exit("You need to grant root privileges to run this script.")
        xterm_check = subprocess.run('which xterm',
                                     shell=True,
                                     stderr=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL)
        if xterm_check.returncode != 0:
            print(f"{bcolors.WARNING} Package 'xterm' is required to run this application."
                  f"\n (try: sudo apt-get Install xterm) {bcolors.ENDC}")
            exit()

    tittlebar()
    prerequisite_check()
    tittlebar2()
    selection = menu()
    if selection == 0:
        selection = menu()
    if selection == 1:
        instructions()
    if selection == 2:
        attack()

    print("     Re-enabling Linux's automatic suspend:", end=" ", flush=True)
    process = subprocess.run('systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target',
                             shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    if process.returncode == 0:
        print('{:>41}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>41}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(
            f"{bcolors.WARNING} [!] Failed to automatically enable Auto-Suspend. Enable it manually.{bcolors.ENDC}")


def menu():
    print(f"{bcolors.OKGREEN}{bcolors.ENDC}", end="")
    print("     [0] MENU:")
    print("     ─────────────────────────────────────────")
    print("     [1] Instructions and legal cautions.")
    print("     [2] WiFi Disbale & Wait attack.")
    print("     [3] Temporary WiFi access denial attack.")
    print("     [4] Exit.")
    selection = int(input(" [?] Select> ([0] for Menu): "))
    return selection


def tittlebar():
    linux_user = os.getlogin()  # gets user account name
    print("\033c", end="")
    rows = 40
    cols = 100
    os.system("resize -s {row} {col}".format(row=rows, col=cols))
    print()  # add blank line
    print(banner.banner)
    print()
    print("     Application is executed by user:", linux_user, "(press 'Ctrl+C' to stop) \n")
    print(f"{bcolors.WARNING} [!] CAUTION: {bcolors.ENDC}")
    print(f"{bcolors.WARNING}     This tool provides a very offensive penetration test on wireless networks {bcolors.ENDC}")
    print(f"{bcolors.WARNING}     That may result in serious legal consequences in case of unauthorised use {bcolors.ENDC}")
    print(f"{bcolors.WARNING}     We strongly recommend get aware of Radio Communication regulations {bcolors.ENDC}")
    print(f"{bcolors.WARNING}     within your home state. {bcolors.ENDC}")
    print(f"{bcolors.WARNING}     Developer of this tool accepts zero responsibility in case of any abuse. {bcolors.ENDC}")
    confirmation = input("     Please confirm you have read and accept the Caution section above:  (y/n) ")
    if confirmation != "y":
        print("  Exiting...")
        exit()
    print()  # adds extra line


def tittlebar2():
    print("\033c", end="")
    os.system('resize -s 40 95')
    print()  # add blank line
    print(banner.banner2)
    print(f"{bcolors.OKGREEN}{bcolors.ENDC}")


def prerequisite_check():
    global token
    global card
    print(f"{bcolors.BOLD} [i] Initializing prerequisites...(Please Wait){bcolors.ENDC}")
    print()  # blank line
# checking if OS is Linux=================================================================
    print("     Checking if OS is Linux:", end=" ", flush=True)
    if platform.system() != "Linux":
        check_pass = False
        print('{:>55}'.format(f"{bcolors.WARNING} FAILD {bcolors.ENDC}"))
        print(" [!] This tool is designed to work only on linux")
        exit("Exiting...")
    else:
        print('{:>55}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
# checking internet connection=============================================================
    print("     Checking Internet connection:", end=" ", flush=True)
    repo_check = subprocess.run('ping www.google.com -c 4',
                                shell=True,
                                stderr=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL)
    if repo_check.returncode == 0:
        print('{:>50}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>50}'.format(f"{bcolors.WARNING} FAILD {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Internet is not connected. {bcolors.ENDC}",)
        exit("Exiting...")
# updating repo package list:==============================================================
    print("     Updating package list:", end=" ", flush=True)
    repo_check = subprocess.run('sudo apt-get update -y',
                                shell=True,
                                stderr=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL)
    if repo_check.returncode == 0:
        print('{:>57}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>57}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Sources.list is Faulty or unsupported Linux distribution.'. {bcolors.ENDC}", end=" ")
        exit("Exiting...")

# checking aircrack-ng installation:===================================================================
    print("     Checking if Aircrack-ng is installed:", end=" ", flush=True)
    package_check = subprocess.run('which airodump-ng aircrack-ng aireplay-ng airmon-ng',
                                   shell=True,
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)
    if package_check.returncode == 0:
        print('{:>42}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>42}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Aircrack-ng seems not properly installed, \n"
              f"     Attempt to perform automatic installation? (y/n).{bcolors.ENDC}", end=" ")
        auto_installer = input()
        if auto_installer == 'y':
            print(" [i] Preparing to install; Please wait...")
            process = subprocess.run('sudo apt-get install aircrack-ng -y', shell=True,
                                     stdout=subprocess.DEVNULL)
            if process.returncode == 0:
                print("     Checking if installation was successful:", end=" ", flush=True)
                package_check = subprocess.run('which airodump-ng aircrack-ng aireplay-ng airmon-ng',
                                               shell=True,
                                               stdout=subprocess.DEVNULL)
                if package_check.returncode == 0:
                    print('{:>40}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
                    print(f"{bcolors.OKBLUE} [i] Aircrack-ng has been successfully installed. {bcolors.ENDC}")
                else:
                    print(f"{bcolors.WARNING} [!] Aircrack-ng Automatic installation Failed \n"
                          f"     Please re-install it manually.{bcolors.ENDC}",)
                    exit("     Exiting...")
            else:
                print('{:>40}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
                print(f"{bcolors.WARNING} [!] it seems we could NOT perform automatic installation, \n"
                      f"     Please try to install it manually.{bcolors.ENDC}")
                exit("     Exiting...")
        else:
            print(" [i] Aircrack-ng is required to continue. ")
            exit("Exiting...")

# checking macchanger instalation=========================================================================
    print("     Checking if Macchanger is installed:", end=" ", flush=True)
    process = subprocess.run('which macchanger',
                             shell=True,
                             stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
    if process.returncode == 0:
        print('{:>43}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>43}'.format(f"{bcolors.WARNING} FAILD {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Macchanger seems not properly installed.\n"
              f"     Attemp to perform automatic installation? (y/n).{bcolors.ENDC}",end=" ")
        auto_installer = input()
        if auto_installer == 'y':
            print(" [i] Preparing to install; Please wait...")
            mac_changer = subprocess.run('sudo apt-get install macchanger -y',
                                         shell=True,
                                         stderr=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL)
            if mac_changer.returncode == 0:
                print("     Checking if instalation was succesfull:", end=" ", flush=True)
                package_check = subprocess.run('which macchanger',
                                               shell=True,
                                               stderr=subprocess.DEVNULL,
                                               stdout=subprocess.DEVNULL)
                if package_check.returncode == 0:
                    print('{:>40}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
                    print(f"{bcolors.OKBLUE} [i] Macchanger has been succesfully installed. {bcolors.ENDC}")
                else:
                    print(f"{bcolors.WARNING} [!] Macchanger Automatic instalation Failed \n"
                          f"     Please re-install it manually.{bcolors.ENDC}",)
                    exit("     Exiting...")
            else:
                print('{:>40}'.format(f"{bcolors.WARNING} FAILD {bcolors.ENDC}"))
                print(f"{bcolors.WARNING} [!] it seems we could NOT perform automatic installation, \n"
                      f"     Please try to install it manually.{bcolors.ENDC}")
                exit("     Exiting...")
        else:
            print(" [i] Macchanger is required to continue. ")
            exit("     Exiting...")
# checking netifaces instalation=================================
    print("     checking if module Netifaces is available:", end=" ", flush=True)
    try:
        from netifaces import interfaces
    except ImportError:
        print('{:>37}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Netfaces seems not been installed.\n"
              f"     Attempt to perform automatic installation? (y/n).{bcolors.ENDC}",end=" ")
        auto_installer = input()
        if auto_installer == 'y':
            print(" [i] Preparing to install; Please wait...")
            netifaces_installer = subprocess.run('sudo pip3 install netifaces',
                                                 shell=True,
                                                 stderr=subprocess.DEVNULL,
                                                 stdout=subprocess.DEVNULL)
            if netifaces_installer.returncode == 0:
                print(" [i] Netfaces successfully installed.")
                try:
                    from netifaces import interfaces
                except ImportError:
                    print(f"{bcolors.WARNING} [!] Netifaces automatic installation Failed! \n"
                          f"     Please re-install it manually.{bcolors.ENDC}", )
                    exit("     Exiting...")
        else:
            print(" [!] Netifaces is required,you can install it manually (pip install netifaces). ")
    else:
        print('{:>37}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))

# detecting wireless device=====================================================
    print("     Detecting wireless cards...", end=" ", flush=True)
    print('{:>52}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    from netifaces import interfaces
    wificards = interfaces()
    if len(wificards) > 1:
        print(" [i] There are probably more than one wifi card available for use.")
        print("     We need a card supporting packet injection capability.\n")
        for card_number in range(1, len(wificards)):
            print("     [", card_number, "] ", wificards[card_number], sep="")
        print("\n [?] Enter the wireless card number to continue:",end=" ")
        selected_card_number = int(input())
        card = str(wificards[selected_card_number])

    elif len(wificards) == 1:
        card = str(wificards[0])

    else:
        print(f"{bcolors.WARNING} [!] there is no wireless card available on your device.{bcolors.ENDC}")
        exit("     exiting...")
# disabling automatic suspend:=======================================================================
    print("     Temporarily disabling Linux's automatic suspend:", end=" ", flush=True)
    process = subprocess.run('sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target',
                             shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    if process.returncode == 0:
        print('{:>31}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>31}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] Failed to automatically disable Auto-Suspend. Please manually disable it.{bcolors.ENDC}")
# puting wifi device to monitor =========================================================

    print("     killing conflicting processes...", end=" ", flush=True)
    check_kill = subprocess.run('sudo airmon-ng check kill', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if check_kill.returncode == 0:
        print('{:>47}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>47}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        exit(" [i] Failed to kill conflicting processes, Contact the developer for help.")
# rfkilling==================================================================
    print("     Performing RF-kill unblocking...", end=" ", flush=True )
    rf_kill = subprocess.run('sudo rfkill unblock all', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if rf_kill.returncode == 0:
        print('{:>47}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>47}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        exit(" [i] Failed to unblock RF-KILL, Contact the developer for help.")
# monitor mode===========================================================================
    print("     Setting up Monitor mode...", end=" ", flush=True)
    monitor_mode = subprocess.run('sudo iw dev ' + str(card) + ' set type monitor', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if monitor_mode.returncode == 0:
        print('{:>53}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>53}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        exit(" [i] Failed to put WiFi card to Monitor Mode, Contact the developer for help.")
# checking internet connection==============================================================
    print("     Checking Internet connection...(Please wait)", end=" ", flush=True)
    time.sleep(2)
    net_check = subprocess.run('ping www.google.com -c 4',
                               shell=True,
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL)
    if net_check.returncode == 0:
        print('{:>35}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
    else:
        print('{:>35}'.format(f"{bcolors.WARNING} FAILED {bcolors.ENDC}"))
        print(f"{bcolors.WARNING} [!] LAN Internet is not connected. and your WiFi card is on Monitor Mode {bcolors.ENDC}",)
        exit("Exiting...")
# setting notification server============================================================================
    if os.path.isfile("verified") is True:
        print(" [i] You have already verified, Would you like to re-verify?(y/n)", end=" ")
        prompt = input()
        if prompt == "n":
            token_file = open("verified", "r")
            token = token_file.readline().strip()
            pushbullet_message("You are already verified.")
            return
    print(f"{bcolors.BOLD} [i] Setting up notification infrastructures... {bcolors.ENDC}")
    print(f"{bcolors.BOLD} [i] We need to send you notifications to your phone via a tool called Pushbullet{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     built-in Pushbullet API enabled us to send push notifications to any phones.{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     powered by Android or iOS.so we will need a Pushbullet account and application{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     Pushbullet can be signed up for a free at https://www.pushbullet.com .{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     once you signed-up and installed phone application. We need your account token{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     to be able to send you notifications. {bcolors.ENDC}")
    print(f"{bcolors.WARNING} [!] your Pushbullet token will be stored locally in current directory.{bcolors.ENDC}")
    print(f"{bcolors.WARNING}     Please be aware that it must not be shared with anyone.{bcolors.ENDC}")
    print(f"{bcolors.BOLD}     Token can be obtained at: https://www.pushbullet.com/#settings  .{bcolors.ENDC}")
    print()
    print(" [?] Enter your Pushbullet Token:")
    token = input("     TOKEN: ")

    print(f"{bcolors.WARNING} [!] Please install Pushbullet app on your phone and sign in to you account. {bcolors.ENDC}")
    print(f"{bcolors.WARNING} [i] Press Enter to continue once you done installation. {bcolors.ENDC}", end=" ")
    input()
    verification_succeed = False
    while verification_succeed is False:
        print(" [i] Enter verification code you received via notification on your phone.  ")
        verification_code = randint(100000,999999)
        message = " Your verification code is: " + str(verification_code)
        pushbullet_message(message)
        user_entered_verification = input("     Code:")
        if user_entered_verification == str(verification_code):
            print(f"{bcolors.OKBLUE} [i] Verification Succeed!{bcolors.ENDC}")
            verification_succeed = True
            token_file = open("verified", "w")
            token_file.write(str(token))
            token_file.close()
            pushbullet_message("Verification Succeed!")
        else:
            print(f"{bcolors.WARNING} [!] Wrong verification code! please retry.{bcolors.ENDC}")


def attack():
    global target_bssid
    global target_pwr
    global target_ch
    global target_essid
    global card
    global token


    tittlebar2()
    print(f"{bcolors.BOLD} [i] Gathering WiFi networks identities...{bcolors.ENDC}", end="", flush=True)
    pushbullet_message("Gathering WiFi networks identities")
    airodump_ng = subprocess.Popen(['sudo airodump-ng ' + str(card)],
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True,
                                   shell=True,
                                   preexec_fn=os.setsid)
    print("(Wait 35 s)", end=" ",)
    timeout = int(time.time()) + 35  # 35 secconds from now
    while True:
        return_code = airodump_ng.poll()
        output = airodump_ng.stdout.readline()
        if output[3] == ":" and output[22] != ":":
            target = target_reader(output)
            if target.bssid not in target_bssid:
                target_bssid.append(target.bssid)
                target_pwr.append(target.pwr)
                target_ch.append(target.ch)
                target_essid.append(target.essid)
        if return_code is not None or (int(time.time()) > timeout):
            break
    os.killpg(os.getpgid(airodump_ng.pid), signal.SIGTERM)

    if len(target_essid) > 0:
        print('{:>32}'.format(f"{bcolors.OKBLUE} SUCCEED {bcolors.ENDC}"))
        print()
        print(" [i] Total", len(target_bssid), " targets have been detected.", flush=True)
    else:
        exit("\n [!] there are some unknown errors.Exiting...,")
    print("\n [i] listing targets...")
    total_target_number = len(target_bssid)
    for i in range(total_target_number):
        print("     (",i ,") ", "Signal power: ", target_pwr[i], " BSSID/Name: ", target_bssid[i], " ",target_essid[i], sep="")

    print(f"{bcolors.WARNING} [!] Enter chosen AP number(s) carefully separated by space:{bcolors.ENDC}")
    selected_targets_number = selector(total_target_number)


    with open('variables.pkl', 'wb') as f:
        pickle.dump([selected_targets_number, target_bssid, target_essid, target_ch, card, token], f)

    #/////////////////////////////////////////////////////////////////////////////

    print(f"{bcolors.WARNING} [!] Attack is being started in few seconds...:{bcolors.ENDC}")
    print(f"{bcolors.WARNING} [i] You will be informed of upcoming events both by log list below and :{bcolors.ENDC}")
    print(f"{bcolors.WARNING}     mobile notifications... :{bcolors.ENDC}")
    time.sleep(2)
    print(f"{bcolors.BOLD} [I] SYSTEM LOG:{bcolors.ENDC}")
    print(f"{bcolors.BOLD} ─────────────────────────────────────── {bcolors.ENDC}")
    print(" [i] Preparing to start services...", flush=True)
    internet_module = subprocess.Popen(['sudo ./internet_module.py'],
                                       stdout=sys.stdout,
                                       shell=True,
                                       preexec_fn=os.setsid)

    monitor_module = subprocess.Popen(['sudo ./monitor_module.py'],
                                      stdout=sys.stdout,
                                      shell=True,
                                      preexec_fn=os.setsid)

    attack_module = subprocess.Popen(['sudo ./attack_module.py'],
                                     stdout=sys.stdout,
                                     shell=True,
                                     preexec_fn=os.setsid)
    try:
        while True:
            if internet_module.poll() is not None:
                print(f"{bcolors.WARNING} [!] Error: file internet_module.py crashed!:{bcolors.ENDC}")
                try:
                    os.killpg(os.getpgid(internet_module.pid), signal.SIGTERM)
                    internet_module = subprocess.Popen(['sudo ./internet_module.py'],
                                                       stdout=sys.stdout,
                                                       shell=True,
                                                       preexec_fn=os.setsid)
                except ProcessLookupError:
                    internet_module = subprocess.Popen(['sudo ./internet_module.py'],
                                                       stdout=sys.stdout,
                                                       shell=True,
                                                       preexec_fn=os.setsid)
                time.sleep(2)
                if internet_module.poll() is None:
                    print(f"{bcolors.OKBLUE} [i] File internet_module.py has been recovered.\n"
                          f"     No further actions is needed.:{bcolors.ENDC}")
                else:
                    print(
                        f"{bcolors.WARNING}    Critical Error: Internet module failed. contact Leukosyte Social:{bcolors.ENDC}")

            if monitor_module.poll() is not None:
                print(f"{bcolors.WARNING} [!] Error: file monitor_module.py crashed!:{bcolors.ENDC}")
                try:
                    os.killpg(os.getpgid(monitor_module.pid), signal.SIGTERM)
                    monitor_module = subprocess.Popen(['sudo ./monitor_module.py'],
                                                      stdout=sys.stdout,
                                                      shell=True,
                                                      preexec_fn=os.setsid)
                except ProcessLookupError:
                    monitor_module = subprocess.Popen(['sudo ./monitor_module.py'],
                                                      stdout=sys.stdout,
                                                      shell=True,
                                                      preexec_fn=os.setsid)
                time.sleep(2)
                if monitor_module.poll() is None:
                    print(f"{bcolors.OKBLUE} [i] File monitor_module.py has been recovered.\n"
                          f"     No further actions is needed.:{bcolors.ENDC}")
                else:
                    print(
                        f"{bcolors.WARNING}     Critical Error: Monitor module failed! contact Leukosyte Social:{bcolors.ENDC}")

            if attack_module.poll() is not None:
                print(f"{bcolors.WARNING} [!] Error: file attack_module.py just crashed!:{bcolors.ENDC}")
                try:
                    os.killpg(os.getpgid(attack_module.pid), signal.SIGTERM)
                    attack_module = subprocess.Popen(['sudo ./attack_module.py'],
                                                     stdout=sys.stdout,
                                                     shell=True,
                                                     preexec_fn=os.setsid)
                except ProcessLookupError:
                    attack_module = subprocess.Popen(['sudo ./attack_module.py'],
                                                     stdout=sys.stdout,
                                                     shell=True,
                                                     preexec_fn=os.setsid)

                time.sleep(2)
                if attack_module.poll() is None:
                    print(f"{bcolors.OKBLUE} [i] File attack_module.py has been recovered.\n"
                          f"     No further actions is needed.:{bcolors.ENDC}")
                else:
                    print(f"{bcolors.WARNING}    Critical Error: Attack module failed! contact Leukosyte Social:{bcolors.ENDC}")

    except KeyboardInterrupt:
        print(" [i] Stopping services...")
        print("exiting")
        os.killpg(os.getpgid(internet_module.pid), signal.SIGTERM)
        os.killpg(os.getpgid(monitor_module.pid), signal.SIGTERM)
        os.killpg(os.getpgid(attack_module.pid), signal.SIGTERM)
        sys.exit()


main()
