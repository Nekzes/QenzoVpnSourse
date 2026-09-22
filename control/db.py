import sqlite3
import json
import os

class DatabaseUsers():

    def __init__(self,db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.Cache = {}

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            username TEXT,
            tariff TEXT,
            tg_id TEXT,
            used_promo TEXT)""")
        
        self.conn.commit()
        return True
    def add_user(self,email : str,password : str, username: str = "-",tariff : str = '-',tg_id : str = "-",used_promo : str = ""):
        try:
            self.cursor.execute("""INSERT INTO users (email,password,username,tariff,tg_id,used_promo)
            VALUES (?,?,?,?,?,?)""",(email,password,username,tariff,tg_id,used_promo))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"DB SDK: {e}")
            return False
        
    def update_data(self, column,email,value) -> bool:
        allowed_fields = ["email","password","username","tariff","tg_id","used_promo"]
        if column not in allowed_fields: return False
        try:
            query = f"UPDATE users SET {column} = ? WHERE email = ?"
            self.cursor.execute(query,(value,email))
            self.conn.commit()
            return True
        except Exception as e:
            return False
        
    def _get_used_promo(self,email : str):
        try:
            self.cursor.execute("""SELECT used_promo FROM users WHERE email = ?""",(email))
            data = self.cursor.fetchone()[0].split(",")
            return data
        except Exception as e:
            return False

    def _save_used_promo(self,email : str, promocodes : list):
        total_str = ""
        for indx,elem in enumerate(promocodes):
            if indx == 0:
                total_str.join(elem)
                continue
            total_str.join(f".{elem}")
        self.update_data(email=email,column="used_promo",value=total_str)
        return True
    
    def use_promo(self,email : str ,promoname : str):
        self._save_used_promo(email=email,promocodes=(self._get_used_promo(email=email).append(promoname)))
        return True
    
    def is_used_promo(self,email : str, promocodename : str) -> bool:
        data = self._get_used_promo(email=email)
        if data is bool: return False
        if promocodename in data: return False
        else: return False

    def get_data(self,email : str):
        try:
            self.cursor.execute("""SELECT * FROM USERS WHERE email = ?""",(email,))
            data = self.cursor.fetchone()
            json_format = {
                "id" : data[0],
                "email" : data[1],
                "password" : data[2],
                "username" : data[3],
                "tariff" : data[4],
                "tg_id" : data[5]
            }
            print(json_format)
            return json_format
        except Exception as e:
            print(f"DB SDK:: {e}")
            return False

    def is_client(self, email: str = None, tg_id: str = None) -> bool:
        try:
            if email: self.cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            elif tg_id: self.cursor.execute("SELECT 1 FROM users WHERE tg_id = ?", (tg_id,))
            else: return False 
            result = self.cursor.fetchone()
            return bool(result) 

        except Exception as e:
            return False

    def close(self):
        self.conn.close()

class DatabasePromocodes():
    def __init__(self,path : str):
        self.path = path

    def add_promocode(self,promoname : str, plus_type : str,under_plus_type : str,value_plus : int) -> bool:
        if plus_type not in ["def","wl"]: return False
        if under_plus_type not in ["gb"]: return False
        promocodes = self._get_promocodes()
        promocodes[promoname] = f"{plus_type}.{under_plus_type}.{value_plus}"
        self._save_promocodes(promocodes)
        return True
    
    def remove_promocode(self,promoname : str) -> bool:
        data = self._get_promocodes().get(promoname)
        if data == None: return False
        del data[promoname]
        self._save_promocodes(data=data)
        return True
    
    def get_promo(self,promoname : str):
        data = self._get_promocodes().get(promoname)
        if data == None: return False
        print("ДАнные промоо из бд ", data)
        promo_data = data.split(".")
        plus_type = promo_data[0]
        under_plus_type = promo_data[1]
        value_plus_type = promo_data[2]
        return (plus_type,under_plus_type,value_plus_type)
    
    def _get_promocodes(self):
        if not os.path.exists(self.path):
            print('PATH NOT FOUND')
            return False
        if os.path.exists(self.path):
            with open(self.path,'r',encoding='utf-8') as f:
                return json.load(f)
        else:
            return False
    def _save_promocodes(self,data : dict) -> bool:
        try:
            with open(self.path,'w',encoding='utf-8') as f:
                json.dump(data,f)
                return True
        except:
            return False