from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import config

from sdk import control

cache = {}

app = Flask(__name__)
app.secret_key = config.FlaskSetting.SECRET_KEY

conSDK = control.ControlSDK()


#MAIN HENDLER

@app.route('/',methods=["GET"])
def main_hendler():
    return render_template("index.html")

# API HENDLERS

@app.route('/api/reg', methods=["POST"])
def reg():
    email = request.form.get("email")
    password = request.form.get("password")
    answ = conSDK.reg(email=email,password=password)
    if answ is not True:
        return jsonify({
            "status" : False,
            "error": "Ошибка регистрации"
        }) #скорее всего такой пользователь уже есть
    else:
        print(f"ANSW REG: {answ}")
        return jsonify({
            "status" : True,
            "des" : "Пользователь успешно зарегистрирован"
        })

@app.route('/api/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        email = session.get("email")
        if email:
            return jsonify({
                "auth": True,
                "user_id" : session.get("email")
            }), 200
        return jsonify({"auth": False, "error": "Необходима авторизация"}), 401
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Ожидается Json"}), 400
        data = request.get_json()
        user_login_mail = data.get('email')
        user_login_password = data.get('password')


        answ = conSDK.login(email=user_login_mail,password=user_login_password)
        print(answ)
        if answ == False:
            print(f"Логин: {user_login_mail}, {user_login_password}")
            return jsonify({
                "status" : False,
                "error": "Необходима регистрация"
            }),401
        if answ == True:
            print("пользоваетль авторизован")
            session["email"] = user_login_mail
            return jsonify({
                "status": True,
                "des" : "Пользователь авторизирован"
            }), 200
        else:
            print(f"Логин: {user_login_mail}, {user_login_password}")
            return jsonify({
                "status": False,
                "error" : "Неверный пароль или логин"
            }), 401


@app.route("/api/traffik", methods=["GET"])
def traffik():
    email = session.get('email')
    req_type = request.args.get("tr_type") #wl для вайт лиcтов / def для обычных подписок 
    if email == None:
        return jsonify({
            "status": False,
            "error" : "Пользователь не авторизован"
        }), 401
    print(f"TRAFIK{req_type}")
    answ = conSDK.get_traffik(email=email,tr_type=req_type)
    if isinstance(answ,tuple):
        usage = answ[0]
        total = answ[1]
        return jsonify({
            "status": True,
            "des": "Трафик успешно получен",
            "usage" : usage,
            "total" : total
        }), 200
    else:
        return jsonify({
                "status": False,
                "error": "Ошибка получения трафика"
        }), 502
    # если статус False то значит что у пользователя нет подписки


@app.route("/api/sublink", methods=["GET"])
def sub_link():
    email = session.get('email')
    print(f"SUB {email}")
    req_type = request.args.get("tr_type") #wl для вайт лиcтов / def для обычных подписок 
    if email == None:
        return jsonify({
            "status": False,
            "error" : "Пользователь не авторизован"
        }), 401
    answ = conSDK.get_sublink(email=email,tr_type=req_type)
    if answ not in conSDK.errors_list:
        return jsonify({
                        "status": True,
                        "des": "Ссылка сгенирирована",
                        "sub_link" : answ
                }), 200
    else:
        return jsonify({
                                "status": False,
                                "error": "Ошибка генирации ссылки"
                            }), 502
    # если статус False значит что либо у пользователя нет этой подписки либо ошибка на сервере

@app.route("/api/del",methods=["POST"])
def del_sub():
    email = session.get('email')
    req_type = request.form.get("tr_type") #wl для вайт лиcтов / def для обычных подписок 
    if email == None:
        return jsonify({
                "status": False,
                "error" : "Пользователь не авторизован"
            }), 401
    answ = conSDK.del_client(email=email,tr_type=req_type)
    if answ is not bool:
        return jsonify({
                        "status": False,
                        "error" : "Ошибка удаления пользвателя"
                    }), 502
    else:
        return jsonify({
                    "status": True,
                    "des" : "Пользователь удален"
                }), 200
    # если статус False то скорее всего пользователь не найден в панели это значит что его подписка уже удалена лиюо у него ее нету

@app.route("/api/create_pay",methods=["POST"])
def create_pay():
    print("start generativ")
    email = session.get('email')
    sub_code = request.form.get("sub_code")
    print(sub_code)
    if email == None:
        print('not login')
        return jsonify({
                    "status": False,
                    "error" : "Пользователь не авторизован"
            }), 401
    answ = conSDK.create_pay(email=email,sub_code=sub_code)
    if answ not in conSDK.errors_list:
        return jsonify({
                "status": True,
                "des" : "Платеж создан",
                "pay_link": answ
            }),200
    else:
        return jsonify({
                    "status" : False,
                    "error" : "Неверный sub_code"
                }), 400
    # pay_link может быть None при ошибках сервера

@app.route("/api/webhook",methods=["POST"])
def webhook():
    token = request.headers.get("X-Secret-Key")
    if token != config.WebHook.TOKEN:
        return jsonify({
            "status" : False,
            "error" : "Ошибка запроса 403"
        }), 403
    email = request.form.get('email')
    sub_code = request.form.get('sub')
    tg_id = request.form.get("tg_id")
    cache[email] = {
        'email' : email,
        'sub' : sub_code,
        'tg_id' : tg_id
    }
    return "", 200

@app.route("/api/success_pay",methods=["GET"])
def succes_pay():
    email = session.get('email')
    if email == None:
        return jsonify({
                    "status": False,
                    "error" : "Пользователь не авторизован"
            }), 401
    if cache.get(email) != None:
        del cache[email]
        return jsonify({
            "status" : True,
            "des" : "Трансакция оплачена"
        }),200
    return jsonify({
        "status" : False,
        'error' : "Транзакция не найдена"
    }),404


@app.route('/api/promo',methods=["POST"])
def promo():
    email = session.get('email')
    if email == None:
        return jsonify({
                    "status": False,
                    "error" : "Пользователь не авторизован"
            }), 401
    promocode = request.form.get("promo")
    answ = conSDK.promo(email=email,promo=promocode)
    if answ is not True:
        return jsonify({
                "status" : False,
                "error" : answ
        }),502
    else:
        return jsonify({
            "status" : True,
            "des" : "gb Добавлены при создании"
        }),200
@app.route("/api/exit", methods=["GET"])
def exit():
    session.pop('email', None) 
    session.pop('password', None)
    return jsonify({
        "status": True,
        "des" : "Сессия удалена"
    }), 200