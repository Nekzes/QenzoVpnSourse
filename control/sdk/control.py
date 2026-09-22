from app.web.sdk import config_control
import httpx

class ControlSDK:
    def __init__(self):
        self.headers_key = config_control.Server.SECRET_KEY
        self.base_url = config_control.Server.BASE_URL
        self.httpx_client = httpx.Client(headers={"X-SECRET-API-KEY":self.headers_key})
        self.VERSION = "1.0"
        self.errors_list = ["Ошибка авторизации Api","Пользователь не авторизован","Ошибка генирации ссылки","Неверный sub_code","Ошибка регистрации","Пользователь с такой почтой существует"]

    def is_client_as_email(self,email : str = None) -> bool:
        answer = self.httpx_client.get(
                    url=f"{self.base_url}/api/is_client",
                    params={
                        "email":email
                    })
        answ = answer.json()
        return answ.get("status")

    def is_client_as_tg_id(self,tg_id : str = None):
        answer = self.httpx_client.get(
                    url=f"{self.base_url}/api/is_client",
                    params={
                        "tg_id" : tg_id
                    })
        answ = answer.json()
        return answ.get("status")
    
    def login(self,email : str,password : str):
        answer = self.httpx_client.post(
            url=f"{self.base_url}/api/login",
            json={
                "email":email,
                "password" : password
            })
        answ = answer.json()
        if answ.get("status") == True:
            return True
        else:
            return answ.get("error")

    def reg(self,email : str,password : str):
        answer = self.httpx_client.post(
                    url=f"{self.base_url}/api/reg",
                    json={
                        "email":email,
                        "password" : password
                    })
        answ = answer.json()
        if answ.get("status") == True:
            return True
        else:
            return answ.get("error")

    def update_tg(self,email : str, password : str, tg_id : str):
        answer = self.httpx_client.post(
                            url=f"{self.base_url}/api/update_tg/tg_id",
                            json={
                                "email":email,
                                "password" : password,
                                "tg_id" : tg_id
                            })
        answ = answer.json()
        if answ.get("status") == True:
            return True
        else:
            return answ.get("error")

    def get_traffik(self,email : str ,tr_type : str):
        answer = self.httpx_client.get(
                                    url=f"{self.base_url}/api/traffik",
                                    params={
                                        "email":email,
                                        "tr_type"  : tr_type
                                    })
        answ = answer.json()
        if answ.get("status") == True:
            return (answ.get("usage"), answ.get("total"))
        else:
            return answ.get("error")

    def get_sublink(self,email : str, tr_type : str):
        answer = self.httpx_client.get(
                                    url=f"{self.base_url}/api/sub_link",
                                    params={
                                        "email":email,
                                        "tr_type"  : tr_type
                                    })
        answ = answer.json()
        if answ.get("status") == True:
            return answ.get("sub_link")
        else:
            return answ.get("error")

    def del_client(self,email : str, tr_type: str):
        answer = self.httpx_client.get(
                                    url=f"{self.base_url}/api/del",
                                    params={
                                        "email":email,
                                        "tr_type"  : tr_type
                                    })
        answ = answer.json()
        if answ.get("status") == True:
            return True
        else:
            return answ.get("error")  

    def create_pay(self,email : str,sub_code : str):
        answer = self.httpx_client.post(
                                    url=f"{self.base_url}/api/create_pay",
                                    json={
                                        "email":email,
                                        "sub_code"  : sub_code
                                    })
        answ = answer.json()
        if answ.get("status") == True:
            return answ.get("pay_link")
        else:
            return answ.get("error")

    def promo(self,email : str, promo : str):
        answer = self.httpx_client.get(
                                    url=f"{self.base_url}/api/del",
                                    params={
                                        "email":email,
                                        "promo"  : promo
                                    })
        answ = answer.json()
        if answ.get("status") == True:
            return True
        else:
            return answ.get("error")         
        