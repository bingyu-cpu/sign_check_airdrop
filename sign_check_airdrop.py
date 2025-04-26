import random
import string
import time
import requests
from web3.auto import w3
from eth_account.messages import encode_defunct
import concurrent.futures
import csv
import os  
import threading

def get_signature(evm_private_key, message: str) -> str:
        message = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(message, private_key=evm_private_key)
        signature = signed_message["signature"].hex()
        return signature

class Sign:
    def __init__(self, key, proxy=None):

        self.account = w3.eth.account.from_key(key)
        self.address = self.account.address
        self.private_key = self.account.key


        self.http = requests.Session()
        if proxy:
            self.http.proxies.update(proxy)
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://airdrop.sign.global',
            'priority': 'u=1, i',
            'referer': 'https://airdrop.sign.global/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sid': '',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }


    def login(self):
        timestamp = int(time.time() * 1000)
        msg =  f'AD_xdwdw156ORWh,EVM Wallet,{timestamp}'
        signature = get_signature(self.private_key, msg)

        json_data = {
            'signature': signature,
            'message': msg,
            'key': w3.to_checksum_address(self.address),
            'address':w3.to_checksum_address(self.address),
            'projectId': 'AD_xdwdw156ORWh',
            'timestamp': timestamp,
            'recipientType': 'EVM Wallet',
        }
        res = self.http .post('https://claim.tokentable.xyz/api/airdrop-open/connect-wallet', headers=self.headers, json=json_data)
        # print(res.text)
        if ':true' in res.text:
             sid = res.json()['data']['sid']
             self.http.headers.update({'sid': sid})
             return True
        print(f'{self.address} login >>> {res.text}')
        return False

    def check_airdrop(self):
         
        if not self.login():
            return False

        json_data = {
            'projectId': 'AD_xdwdw156ORWh',
        }
        res = self.http.post('https://claim.tokentable.xyz/api/airdrop-open/check-eligibility', json=json_data)
     
        if ':true' in res.text:
             self.value = 0
             if len(res.json()['data']['claims']) > 0:
                  self.value = int(res.json()['data']['claims'][0]['value']) / 10**18
               
             return True
        print(f'{self.address} check_airdrop >>> {res.text}')
        return False

def get_proxies_brightdata():
    ip = "brd.superproxy.io"
    port = "22225"
    username = ""
    password = ""

    characters = string.ascii_letters + string.digits  # 包括字母和数字
    random_chars = ''.join(random.choice(characters) for _ in range(8))
    session = "-session-" + random_chars

    proxies = {"http": "http://" + username + session + ":" + password + "@" + ip + ":" + port,
               "https": "http://" + username + session + ":" + password + "@" + ip + ":" + port}
    return proxies

def save_text_to_file(content):
    with open(done_address_csv, mode='a+', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(content)

def task(address,private_key):
    try:
        proxy = get_proxies_brightdata()
        sign = Sign(key=private_key, proxy=proxy)
        if not sign.check_airdrop():
           return False
        
        print(f'{address} claim value: {sign.value}')
        with lock:
            save_text_to_file([address,private_key,sign.value])  
        return True
    except Exception as e:
        print(e)
        return False


lock = threading.Lock()
done_address_csv = f'task_info/Sign_check_airdrop_done.csv'

if __name__ == '__main__':
    
        if not os.path.exists('task_info'):
            os.makedirs('task_info')

        done_list = []
        args_list = []
        lines_list = []

        if os.path.exists(done_address_csv):
            with open(done_address_csv, "r", encoding='utf-8') as file:

                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) > 1:
                        done_list.append(row[0])


        with open('111.csv', 'r', encoding='utf-8') as file:
            csv_reader_ = csv.reader(file)
            for row_ in csv_reader_:
                address = row_[0]
                private_key = row_[1]

                if address not in done_list:
                    args_list.append([address,private_key])

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # 提交任务给线程池，map方法中的元组表示每个任务的参数
            executor.map(lambda args: task(*args), args_list)
        


