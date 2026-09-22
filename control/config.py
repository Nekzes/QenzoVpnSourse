class SERVER:
    VERSION = "1.0a"
    SECRET_KEY = 'nek07037'
    
class VpnSDK:
    BASE_URL = "https://vpn.n3k00.ru:7037/nek0"
    SUB_URL = "https://vpn.n3k00.ru:2096"
    TOKEN = ""
    INBOUNDS = [1,2,4,17,18,19]
    USED_TRIALS_FILE = "used_trials.txt"

class WlVpnSDK:
    BASE_URL = "http://158.160.147.14:58667/LLfYxuWha9xJeMiaM8"
    SUB_URL = "http://158.160.147.14:2096"
    TOKEN = ""
    INBOUNDS = [1]

class PaySDK:
    MERCH = ""
    SECRET = ""
    SECRET_SUB_SERVICES_TOKEN = ""
    CURRENCY = "RUB"
    RETURN_LINK = "https://app.n3k00.ru"
    FAILED_LINK = "https://app.n3k00.ru"
    SUB_SERVICE = ['']
    TARIFS = {"pro": {"price": 15,
                        "gb": 15,
                        "metadata" : 'ℹ️ Подписка "🔥 Про" в QenzoVPn👻'},
              "test" : {"price": 1,
                        "gb": 1,
                        "metadata" : 'ℹ️ Подписка "🎯 Тест" в QenzoVPn👻'},
              "whitelist" : {"price":20,
                             "gb": 10,
                             "metadata" : 'ℹ️ Подписка "🌿 WhiteList" в QenzoVPn👻'},
              "ultra": {"price":75,
                        "gb":100,
                        "metadata" : 'ℹ️ Подписка "☄️ Ультра" в QenzoVPn👻'}}
    

class DB:
    PROMO_DATA_PATH = "promo.json"
    USERS_DATA_PATH = "qenzo_users.db"

class FlaskSetting:
    SECRET_KEY = ""