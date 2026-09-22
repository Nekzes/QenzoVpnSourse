import json
import os
import urllib.parse
import httpx
import config

DB_FILE = config.VpnSDK.USED_TRIALS_FILE

def is_trial_used(email):
    if not os.path.exists(DB_FILE):
        return False  
    
    with open(DB_FILE, "r") as f:
        for line in f:
            if str(email) == line.strip():
                return True
    return False


def set_trial_used(email):
    with open(DB_FILE, "a") as f:
        f.write(f"{email}\n")


class API:
    def __init__(self, base_url: str, sub_url:str, token: str,inbounds: list):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.client_httpx = httpx.Client(verify=False)
        self.sub_url = sub_url
        self.inbounds = inbounds

    def clients(self):
        try:
            resp = self.client_httpx.get(f'{self.base_url}/panel/api/clients/list', headers=self.headers)
            return resp.json()
        except Exception as e:
            return e

    def new_client(self, mail, gb):
        try:
            total_gb = int(int(gb) * (1024 ** 3))
            resp = self.client_httpx.post(
                f"{self.base_url}/panel/api/clients/add",
                json={
                    "client": {
                        "email": str(mail),
                        "totalGB": total_gb,
                        "expiryTime": 0,
                        "limitIp": 0,
                        "enable": True
                    },
                    "inboundIds": self.inbounds
                },
                headers=self.headers
            )
            data = resp.json()
            if data.get("seccess") != True:
                return data
            return True
        except Exception as e:
            print(f"Ошибка при создании клиента: {type(e)}")
            return e
        
    def update_gb(self,user_id,gb):
        url_path = f"{self.base_url}/panel/api/clients/update/{user_id}"
        _ , total = self.get_traffik(user_id)
        payload ={
            "email": str(user_id),
            "totalGB": int(((total * (1024 ** 3)) + gb * (1024 ** 3))),
            "tgId": int(user_id),
            "enable": True
            }
        try:
            _ , total = self.get_traffik(user_id)
            resp = self.client_httpx.post(url=url_path,json=payload,headers=self.headers)
            data = resp.json()

            if data['success'] == True:
                return True
            else:
                return False 

        except Exception as e:
            print(f"ERORO UPDATE GB: {data}")
            return False

    def update_tg(self,email,tg_id):
        url_path = f"{self.base_url}/panel/api/clients/update/{email}"
        _ , total = self.get_traffik(email)
        payload ={
            "email": str(email),
            "totalGB": int(total),
            "tgId": int(tg_id),
            "enable": True
            }
        try:
            resp = self.client_httpx.post(url=url_path,json=payload,headers=self.headers)
            data = resp.json()

            if data['success'] == True:
                return True
            else:
                return False 

        except Exception as e:
            print(f"ERORO UPDATE TG: {data}")
            return False



    def is_client(self,mail):
        url = f"{self.base_url}/panel/api/clients/get/{mail}"
        try:
            resp = self.client_httpx.get(url, headers=self.headers)
            data = resp.json()
            if data['success'] is True:
                return True
            else:
                return False
        except Exception as e:
            print(f"ошибка при проверке клиента: {e} , status_code: {resp.status_code}")
            return e
        
    def generate_sub_link(self,mail):
        url = f"{self.base_url}/panel/api/clients/get/{mail}"
        try:
            resp = self.client_httpx.get(url,headers=self.headers)
            data = resp.json()
        except Exception as e:
            print('Ошибка запрса к панели')
            return False
        if not data.get('success'):
            return False
        obj = data['obj']
        sub_id = obj['client']['subId']

        sub_url = f"{self.sub_url}/sub/{sub_id}"
        return sub_url


    
    def get_traffik(self, mail):
        try:
            resp = self.client_httpx.get(f'{self.base_url}/panel/api/clients/traffic/{str(mail)}', headers=self.headers)
            if resp.status_code == 404:
                return (False, False)
            else:
                data = resp.json()
                total = int(data['obj']['total']) / (1024**3)
                usege = (int(data['obj']['up']) + int(data['obj']['down'])) / (1024**3)
                return (round(usege, 2), round(total, 2))
        except Exception as e:
            print(f"Ошибка при получении трафика: {e}")
            return (False,False)
        
    def delete_client(self, email):
        url = f"{self.base_url}/panel/api/clients/del/{email}?keepTraffic=0"
        try:
            resp = self.client_httpx.post(url, headers=self.headers)
            return resp.json()
        except Exception as e:
            return {"success": False, "msg": str(e)}


#bot.py version == 1.0
#hend.py version == 1.0
#vpn_api.py version == 1.0s