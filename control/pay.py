import requests
import json
import config

class API:
    def __init__(self,merch,secret,currency='RUB'):
        self.merch = merch
        self.secret = secret
        self.currency = currency
        self.headers = {
            'X-MerchantId': self.merch,
            'X-Secret': self.secret,
            'Content-Type': 'application/json'
            }
        self.url = "https://app.platega.io"

    def create_invoice(self,amount,description,email,tariff,tg_id='NONE'):
        payload = json.dumps({
            "paymentDetails": {
                "amount": amount,
                "currency": self.currency
            },
            "description": description,
            "return": config.PaySDK.RETURN_LINK,
            "failedUrl": config.PaySDK.FAILED_LINK,
            "payload": f"{tariff},{email},{tg_id}",
            "metadata": {
                "userID": str(email),
                "userName": str(tariff),
            }
            })
        response = requests.post(url=f"{self.url}/v2/transaction/process", headers=self.headers, data=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return False
        
    def check_invoice(self,Id):
        response = requests.get(url=f'{self.url}/transaction/{Id}',headers=self.headers)
        if response.status_code == 200 and response.json().get("status") == "CONFIRMED": return True
        else: return False

    