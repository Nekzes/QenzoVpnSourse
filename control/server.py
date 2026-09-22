from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import httpx
import datetime
import config
import db
import vpn
import pay

app = Flask(__name__)
app.secret_key = config.FlaskSetting.SECRET_KEY

database_users = db.DatabaseUsers(config.DB.USERS_DATA_PATH)
database_promo = db.DatabasePromocodes(config.DB.PROMO_DATA_PATH)

def_api = vpn.API(config.VpnSDK.BASE_URL,
                  config.VpnSDK.SUB_URL,
                  config.VpnSDK.TOKEN,
                  config.VpnSDK.INBOUNDS
)

wl_api = vpn.API(config.WlVpnSDK.BASE_URL,
                config.WlVpnSDK.SUB_URL,
                config.WlVpnSDK.TOKEN,
                config.WlVpnSDK.INBOUNDS
)

pay_sdk = pay.API(merch=config.PaySDK.MERCH,
                  secret=config.PaySDK.SECRET,
                  currency=config.PaySDK.CURRENCY
)


# API HENDLERS
@app.route("/version",methods=["GET"])
def version():
    return config.SERVER.VERSION

@app.route("/api/is_client",methods=["GET"])
def is_client():
    data = request.get_json()
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
             return jsonify({
                 "status" : False,
                 "error" : "Ошибка авторизации Api"
             }), 403
    if data.get('email') == None: pass
    else:
        find_res = database_users.is_client(email=data.get("email"))
        return jsonify({
            "status" : find_res,
            "des" : "?"
        }),200

    if data.get('tg_id') == None: pass
    else:
        find_res = database_users.is_client(email=data.get("tg_id"))
        return jsonify({
                    "status" : find_res,
                    "des" : "?"
                }),200



@app.route("/api/reg",methods=["POST"])
def reg():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
        return jsonify({
            "status" : False,
            "error" : "Ошибка авторизации Api"
        }), 403
    data = request.get_json()
    user_reg_mail = data.get('email')
    user_reg_password = data.get('password')
    if database_users.is_client(email=user_reg_mail):
        return jsonify({
            "status" : False,
            "erorr" : "Пользователь с такой почтой существует"
        }), 404
    req = database_users.add_user(email=user_reg_mail,password=user_reg_password)
    print(f"CREATE USER {req}")
    if req == True:
        return jsonify({
            'status' : True,
            'des' : "Пользователь успешно зарегистрирован"
        }), 200
    return jsonify({
         "status" : False,
         "erorr" : "Ошибка регистрации"
    }), 502

@app.route("/api/update/tg_id",methods=["POST"])
def update_tg_id():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
        return jsonify({
                 "status" : False,
                 "error" : "Ошибка авторизации Api"
        }), 403
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    tg_id = data.get("tg_id")
    if database_users.is_client(email=email) != True:
        return jsonify({
                "status" : False,
                "erorr" : "Отсутсвует регистрация"
            }), 404

    if database_users.get_data(email=email).get("password") != password:
        return jsonify({
            "status" : False,
            "erorr" : "Неверный пароль"
        }),403

    req = database_users.update_data("tg_id",email=email,value=tg_id)
    if req:
        return jsonify({
                    "status": True,
                    "des" : "Пользовательские данные обновлены"
                }), 200
    return jsonify({
                "status" : False,
                "erorr" : "Ошибка обновления"
            }),502

@app.route('/api/login', methods=["POST"])
def login():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
        return jsonify({
            "status" : False,
            "error" : "Ошибка авторизации Api"
        }),403
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Ожидается Json"}), 400
        data = request.get_json()
        user_login_mail = data.get('email')
        user_login_password = data.get('password')

        if  database_users.is_client(email=user_login_mail) == False:
            return jsonify({
                "status" : False,
                "error": "Необходима регистрация"
            }),401
        if database_users.get_data(user_login_mail).get("password") == None:
            return jsonify({
                "status": False,
                "error": "Необходимо получение пароля"
                }),401
        if database_users.get_data(user_login_mail).get("password") == user_login_password:
            return jsonify({
                "status": True,
                "des" : "Пользователь авторизирован"
            }), 200
        else:
            return jsonify({
                "status": False,
                "error" : "Неверный пароль или логин"
            }), 401


@app.route("/api/traffik", methods=["GET"])
def traffik():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
            return jsonify({
                "status" : False,
                "error" : "Ошибка авторизации Api"
            }), 403

    email = request.args.get('email')
    req_type = request.args.get("tr_type")  #wl для вайт лиcтов / def для обычных подписок 
    print(f"TRAFIK: {email}, {req_type}")
    if email == None:
        return jsonify({
            "status": False,
            "error" : "Пользователь не авторизован"
        }), 401
    if req_type == "wl":
        usage, total = wl_api.get_traffik(email)
        if usage == 'ERORR':
            return jsonify({
                "status": False,
                "error": "Ошибка получения трафика"
            }), 502
        return jsonify({
            "status": True,
            "des": "Трафик успешно получен",
            "usage" : usage,
            "total" : total
        }), 200
    
    if req_type == "def":
        usage, total = def_api.get_traffik(email)
        if usage == 'ERORR':
            return jsonify({
                    "status": False,
                    "error": "Ошибка получения трафика"
                }), 502
        return jsonify({
                "status": True,
                "des": "Трафик успешно получен",
                "usage" : usage,
                "total" : total
            }), 200
    else:
        print(req_type)
        return jsonify({
                    "status": False,
                    "error": "Ошибка неизвестный tr_type"
                    }), 404
    # если статус False то значит что у пользователя нет подписки


@app.route("/api/sublink", methods=["GET"])
def sub_link():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
            return jsonify({
                "status" : False,
                "error" : "Ошибка авторизации Api"
            }), 403
    email = request.args.get('email')
    req_type = request.args.get("tr_type") #wl для вайт лиcтов / def для обычных подписок 
    print(f"SUBLINK: {email}, {req_type}")

    if email == None:
        print('ЕМЭиЛ 00000')
        return jsonify({
            "status": False,
            "error" : "Пользователь не авторизован"
        }), 401
    if req_type == "wl":
            sub_link = wl_api.generate_sub_link(email)
            if sub_link == None:
                return jsonify({
                    "status": False,
                    "error": "Ошибка генирации ссылки"
                }), 502
            return jsonify({
                "status": True,
                "des": "Ссылка сгенирирована",
                "sub_link" : sub_link
            }), 200
    if req_type == "def":
        sub_link = def_api.generate_sub_link(email)
        if sub_link == None:
                return jsonify({
                        "status": False,
                        "error": "Ошибка генирации ссылки"
                    }), 502
        return jsonify({
                    "status": True,
                    "des": "Ссылка сгенирирована",
                    "sub_link" : sub_link
                }), 200
    else:
        print(req_type)
        return jsonify({
                "status": False,
                "error": "Ошибка неизвестный tr_type"
                }), 404
    # если статус False значит что либо у пользователя нет этой подписки либо ошибка на сервере

@app.route("/api/del",methods=["POST"])
def del_sub():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
            return jsonify({
                "status" : False,
                "error" : "Ошибка авторизации Api"
            }), 403
    data = request.get_json()
    email = data.get('email')
    req_type = data.get("tr_type") #wl для вайт лиcтов / def для обычных подписок 
    if email == None:
        return jsonify({
                "status": False,
                "error" : "Пользователь не авторизован"
            }), 401
    if req_type == "wl":
        del_req = wl_api.delete_client(email=email)
        if del_req.get("success") == True:
            return jsonify({
                "status": True,
                "des" : "Пользователь удален"
            }), 200
        return jsonify({
                "status": False,
                "error" : "Ошибка удаления пользвателя"
            }), 502
    if req_type == "def":
        del_req = def_api.delete_client(email=email)
        if del_req.get("success") == True:
            return jsonify({
                "status": True,
                "des" : "Пользователь удален"
            }), 200
        return jsonify({
                "status": False,
                "error" : "Ошибка удаления пользвателя"
            }), 502
    else:
        print('ТР ТАЙП В ДЕЛ')
        return jsonify({
                "status": False,
                "error" : "Неизвестный tr_type"
                }), 404
    # если статус False то скорее всего пользователь не найден в панели это значит что его подписка уже удалена лиюо у него ее нету

@app.route("/api/create_pay",methods=["POST"])
def create_pay():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
            return jsonify({
                "status" : False,
                "error" : "Ошибка авторизации Api"
            }), 403
    print("start generativ")
    data = request.get_json()
    email = data.get('email')
    sub_code = data.get("sub_code")
    print(sub_code)
    tariffs = config.PaySDK.TARIFS
    
    if sub_code not in tariffs:
        print("incorrect sub code",sub_code)
        return jsonify({
            "status" : False,
            "error" : "Неверный sub_code"
        }), 400
    sub_amount = tariffs[sub_code]["price"]
    des = tariffs[sub_code]["metadata"]
    data = database_users.get_data(email=email)
    if data.get("tg_id") == None:
        tg_id = "NONE"
    else:
        tg_id = data.get("tg_id")
    pay_req = pay_sdk.create_invoice(amount=sub_amount,description=des,email=email,tariff=sub_code,tg_id=tg_id)
    print('generate',pay_req)
    return jsonify({
        "status": True,
        "des" : "Платеж создан",
        "pay_link": pay_req.get("url")
    })
    # pay_link может быть None при ошибках сервера

@app.route("/api/webhook",methods=["POST"])
def webhook():
    
    data = request.get_json()
    print(f"CONTROL WEBHOOK: {data}")
    if data['status'] == 'CONFIRMED':
        if pay_sdk.check_invoice(data.get("id")):
            payload = data.get("payload").split(",")
            database_users.Cache[data["id"]] = {
                'trans_id': data.get("id"),
                'sub' : payload[0],
                'email' : payload[1],
                'tg_id' : payload[2],
                'status' : data.get("status"),
                'time': str(datetime.datetime.now())
            }
            print("pay suported")
            successful_pay_hendler(email=payload[1],sub=payload[0],tg_id=payload[2])
            return '', 200
        else:
            return jsonify({
                            "status": False,
                            "error" : "Ошибка"
                            }), 403
    else:
        return '',200
    


@app.route('/api/promo',methods=["POST"])
def promo():
    if request.headers.get("X-SECRET-API-KEY") != config.SERVER.SECRET_KEY:
            return jsonify({
                "status" : False,
                "error" : "Ошибка авторизации Api"
            }), 403
    data = request.get_json()
    email = data.get('email')
    if email == None:
        return jsonify({
                    "status": False,
                    "error" : "Пользователь не авторизован"
            }), 401
    print("Обрабатываем промо")
    promocode = data.get("promo")
    data = database_promo.get_promo(promocode)
    print("получены данные от сдк", data)
    if data != False:
        plus_type = data[0]
        under_type_plus = data[1]
        value_plus = data[2]
        if plus_type == 'gb':
            if under_type_plus == 'wl':
                if wl_api.is_client(email) == True:
                    promo_resp = wl_api.update_gb(email,int(value_plus))
                    if promo_resp != True:
                        return jsonify({
                            "status" : False,
                            "error" : "Ошибка добавления gb"
                        })
                    return jsonify({
                                "status" : True,
                                "des" : "gb Добавлены"
                            })
                    
                else:
                    promo_resp = wl_api.new_client(email,gb=value_plus)
                    if promo_resp == False:
                        return jsonify({
                                "status" : False,
                                "error" : "Ошибка добавления gb при создании"
                                })
                    return jsonify({
                            "status" : True,
                            "des" : "gb Добавлены при создании"
                        })
            if under_type_plus == 'def':
                            if def_api.is_client(email) == True:
                                promo_resp = def_api.update_gb(email,int(value_plus))
                                if promo_resp != True:
                                    return jsonify({
                                                "status" : False,
                                                "error" : "Ошибка добавления gb"
                                        })
                                return jsonify({
                                        "status" : True,
                                        "des" : "gb Добавлены"
                                        })
                            else:
                                promo_resp = def_api.new_client(email,gb=value_plus)
                                if promo_resp == False:
                                    return jsonify({
                                                "status" : False,
                                                "error" : "Ошибка добавления gb при создании"
                                            })
                                return jsonify({
                                            "status" : True,
                                            "des" : "gb Добавлены при создании"
                                        })
    return jsonify({
        "status" : False,
        "error" : "Промокод не найден"
    }), 404
    


def successful_pay_hendler(email : str,sub : str,tg_id : str = None):
    print("HENDELINH PAY ")
    gb = int(config.PaySDK.TARIFS.get(sub).get('gb'))
    if sub == 'whitelist':
        create_client = wl_api.new_client(email,gb=gb)
        if create_client != True:
            print(create_client)
            if create_client.get('msg') == f'Something went wrong (email already in use: {email}\n)':
                print("ошибка выдачи удалем и сосщдаем акк")
                wl_api.delete_client(email=email)
                create_client = wl_api.new_client(email,gb=gb)
                print("создан новый акк после ошибки выдачи")
        else:
            print(create_client)
            print("GB выданы")
            """for i in config.PaySDK.SUB_SERVICE:
                httpx.Client().post(url=i,
                                    headers={"X-SECRET-KEY":config.PaySDK.SECRET_SUB_SERVICES_TOKEN},
                                    json={
                                        "email" : email,
                                        "sub" : sub,
                                        "tg_id" : tg_id})"""
    if sub != 'whitelist':
            create_client = def_api.new_client(email,gb=gb)
            print(create_client)
            if create_client != True:
                print(create_client)
                if create_client.get('msg') == f'Something went wrong (email already in use: {email}\n)':
                    print("ошибка выдачи удалем и сосщдаем акк")
                    def_api.delete_client(email=email)
                    create_client = def_api.new_client(email,gb=gb)
                    print("создан новый акк после ошибки выдачи")
            else:
                print(create_client)
                print("GB выданы")
                """for i in config.PaySDK.SUB_SERVICE:
                    httpx.Client().post(url=i,
                                        headers={"X-SECRET-KEY":config.PaySDK.SECRET_SUB_SERVICES_TOKEN},
                                        json={
                                            "email" : email,
                                            "sub" : sub,
                                            "tg_id" : tg_id})"""
            

    