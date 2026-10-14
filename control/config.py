class SERVER:
    VERSION = "1.0a"
    SECRET_KEY = ''
    
class VpnSDK:
    BASE_URL = ""
    SUB_URL = ""
    TOKEN = ""
    INBOUNDS = [1,2,4,17,18,19]
    USED_TRIALS_FILE = "used_trials.txt"

class WlVpnSDK:
    BASE_URL = ""
    SUB_URL = ""
    TOKEN = ""
    INBOUNDS = [1]

class PaySDK:
    MERCH = ""
    SECRET = ""
    SECRET_SUB_SERVICES_TOKEN = ""
    CURRENCY = "RUB"
    RETURN_LINK = ""
    FAILED_LINK = ""
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
