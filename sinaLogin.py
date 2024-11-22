import json
import os
import re
import sys

sys.path.append("../Service")
import requests
import requests.utils

from Dao.redisDao import redisDao
from Dao.mysqlDao import mysqlDao

import time
from datetime import datetime, timedelta

from setproctitle import setproctitle

import websocket

setproctitle("login")


class weiboLogin(object):

    def __init__(self):

        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

        self.headers = {
            'referer': "https://weibo.com/",
            'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
            'Sec-Ch-Ua-Mobile': "?0",
            'Sec-Ch-Ua-Platform': 'Windows',
            'Sec-Fetch-Dest': "script",
            'Sec-Fetch-Mode': "no-cors",
            'Sec-Fetch-Site': 'cross-site',
            # 'X-Requested-With': 'XMLHttpRequest',
            'User_Agent': self.user_agent,
        }
        self.img_url = None
        self.cookie = ""
        self.sess = None
        self.qrid = None
        self.api_key = None
        self.alt = None

    def getImg(self):
        image_url = "https://login.sina.com.cn/sso/qrcode/image?entry=miniblog&size=180&callback=STK_" + str(
            int(time.time() * 10000))

        self.sess = requests.session()
        res = self.sess.get(image_url, headers=self.headers)
        res.encoding = res.apparent_encoding
        self.api_key = re.search('.*?api_key=(.*)"', res.text).group(1)
        self.qrid = re.search('.*?"qrid":"(.*)?",', res.text).group(1)
        img = 'https://v2.qr.weibo.cn/inf/gen?api_key='
        self.img_url = img + str(self.api_key)

    def checkLoginState(self, openid):
        url = 'https://login.sina.com.cn/sso/qrcode/check?entry=sso&qrid={}&callback=STK_{}'
        tryTime = 0
        dao = redisDao(openid)
        old_urlState = ""

        urlState = ""
        while tryTime < 310:
            '''扫描二维码登录，每隔1秒请求一次扫码状态'''
            response = self.sess.get(url.format(self.qrid, str(int(time.time() * 100000))), headers=self.headers)
            print(response.text)
            data = re.search('.*?\((.*)\)', response.text).group(1)
            data_js = json.loads(data)
            '''
            50114001：二维码未扫描状态
            50114002：二维码已扫描未确认状态
            20000000：二维码已确认状态
            50114004：二维码已失效
            '''
            print(data_js)
            if '50114001' in str(data_js['retcode']):
                urlState = "二维码未使用，请扫码！"
                print('二维码未使用，请扫码！')
            elif '50114002' in str(data_js['retcode']):
                urlState = "已扫二维码，请确认登录！"
                print('已扫码，请点击确认登录！')
            elif '50114004' in str(data_js['retcode']):
                urlState = "二维码已失效，请重新获取！"
                print('该二维码已失效，请重新运行程序！')
            elif '20000000' in str(data_js['retcode']):
                urlState = "登录成功"
                print('登录成功！')
                self.alt = data_js['data']['alt']
                # print(alt)
            else:
                urlState = "二维码出错，请重新获取"
                print('其他情况', str(data_js['retcode']))
            if urlState != old_urlState:
                old_urlState = urlState
                dao.addImgUrl(self.img_url, urlState)
                if urlState == "登录成功" or urlState == "二维码出错，请重新获取" or urlState == "二维码已失效，请重新获取！":
                    break
            imgUrl, state = dao.getImgUrl()
            if state == "" or state is None:
                break
            tryTime += 1
            time.sleep(1)
        # dao.delUrlAndLoginState()

    def initCookie(self):
        alturl = 'https://login.sina.com.cn/sso/login.php?entry=miniblog&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com' \
                 '&alt={}&savestate=30&callback' \
                 '=STK_{}'.format(self.alt, str(int(time.time() * 100000)))
        res = self.sess.get(alturl, headers=self.headers)
        data = re.search('.*\((.*)\);', res.text).group(1)
        print(data)
        data_js = json.loads(data)
        print(data_js)
        # uid = data_js['uid']
        # nick = data_js['nick']
        # print('账户名：' + nick, '\n', 'uid:' + uid)
        crossDomainUrlList = data_js['crossDomainUrlList']
        self.sess.get(crossDomainUrlList[0], headers=self.headers)
        self.sess.get(crossDomainUrlList[1] + '&action=login', headers=self.headers)
        self.sess.get(crossDomainUrlList[2], headers=self.headers)


def loginMain(openid):

    login = weiboLogin()
    while login.img_url is None:
        login.getImg()
    # print(login.img_url)

    login.checkLoginState(openid)

    login.initCookie()

    # print(login.cookie)

    tryMax = 0

    deadTime = datetime.now() + timedelta(days=7) # 保持登录7天

    uid = None
    mdao = mysqlDao(openid)
    rdao = None
    stop = False
    insertLog = True
    while tryMax < 10 and (deadTime - datetime.now()).total_seconds() > 0 and not stop:

        login.sess.get("https://weibo.com/")
        # print(sess.cookies)
        cookie_dict = login.sess.cookies.get_dict()
        # 将cookie转成字典

        superTopicUrl = r"https://weibo.com/p/1008080587fa0e8198ad45108f3a0ef6e08d3a/super_index?display=0&retcode=6102"
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        cookie_string = ""
        for k, v in cookie_dict.items():
            cookie_string += k + '=' + v + ';'
        cookie_string = cookie_string[:-1]
        login.cookie = cookie_string
        headers = {
            'Origin': "https://weibo.com",
            'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'Sec-Ch-Ua-Mobile': "?0",
            'Sec-Ch-Ua-Platform': 'Windows',
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'User_Agent': user_agent,
            'Cookie': cookie_string
        }
        superTopic = requests.get(superTopicUrl, headers=headers)
        rdao = redisDao(openid)

        while "['islogin']='1'" in superTopic.text and not stop:
            weiboUsername = re.findall("\$CONFIG\['nick']='(.*?)';", superTopic.text)[0]
            avatar = re.findall("\$CONFIG\['avatar_large']='(.*?)';", superTopic.text)[0]
            uid = re.findall("\$CONFIG\['uid']='([0-9]*?)';", superTopic.text)[0]
            result = mdao.queryWeibo(uid)
            if result is None:
                mdao.setWeibo(uid, weiboUsername, avatar)
            else:
                if result["avatar"] != avatar:
                    mdao.updateWeibo(uid=uid, state=True, avatar=avatar)
                if result["username"] != weiboUsername:
                    mdao.updateWeibo(uid=uid, state=True, )
            if insertLog:
                insertLog = False
                for taskId in ["task1", "task2", "task3", "task4", "task5"]:
                    mdao.insertIntoWeiboUserLog(uid, weiboUsername, {"finishReason": "未进行过任务"}, taskId)

            rdao.addCookie(uid, login.cookie)
            tryMax = 0
            superTopic = requests.get(superTopicUrl, headers=headers)
            time.sleep(300)
            cookie = rdao.getCookie(uid)

            if (deadTime - datetime.now()).total_seconds() <= 5:
                weiboTaskList = mdao.queryWeiboUserLog(uid)
                additionDay = 0
                for idx, task in enumerate(weiboTaskList):
                    if task["state"] != -1:
                        if idx in [1, 2, 3]:
                            additionDay = max(additionDay, 7)
                        if idx == 4:
                            additionDay = max(additionDay, 1)
                deadTime += timedelta(days=additionDay)

            if cookie == "logout" or cookie == "" or cookie is None:
                login.sess.close()
                stop = True


        time.sleep(5)
        tryMax += 1

    if uid is not None:
        if rdao is not None:
            rdao.addCookie(uid, "logout")
            _delWeiboAllTask(rdao, uid)
        mdao.updateWeibo(uid=uid, state=False)

        for taskId in ["task1", "task2", "task3", "task4", "task5"]:
            _updateTaskLog(mdao, uid, taskId)
            pass

def _delWeiboAllTask(rdao, uid):
    id_tids = rdao.getTid()
    tasks = rdao.getTaskId(uid)
    for task in tasks:
        idTask = uid + "_Task" + task
        if idTask not in id_tids:
            rdao.delTaskId(uid, task)
            continue
        try:
            rdao.delTid(idTask)
            rdao.delTaskId(uid, task)
        except Exception as e:
            pass

def _updateTaskLog(mdao, uid, taskId):

    finishReason = ""
    if taskId == "task1":
        finishReason = "养号已结束"

    if taskId == "task2":
        finishReason = "超话发帖已结束"

    if taskId == "task3":
        finishReason = "转赞评已结束"

    if taskId == "task4":
        finishReason = "转发结束"

    if taskId == "task5":
        finishReason = "定时微博任务已中止"

    data = {
        "state": -1,
        "finishReason": finishReason
    }

    mdao.updateWeiboUserLog(uid, data, taskId)
