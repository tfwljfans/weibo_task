<p align="center">
    <br>
    <img src="./.github/minipg.jpg" width="150"/>
    <br>
<p>
<p align="center">
  <a href="https://app.codacy.com/gh/tfwljfans/weibo_task/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade">
    <img src="https://app.codacy.com/project/badge/Grade/60a36780aa5a4c0588f1afe71a6f838d"
         alt="Codacy Badge">
  </a>
    <a href="https://scan.coverity.com/projects/tfwljfans-weibo_task">
    <img alt="Coverity Scan Build Status"
       src="https://scan.coverity.com/projects/26928/badge.svg"/>
  </a>
    <a href="https://github.com/tfwljfans/weibo_task/stargazers">
    <img src="https://img.shields.io/github/stars/tfwljfans/weibo_task.svg?colorA=orange&colorB=orange&logo=github"
         alt="GitHub stars">
  </a>
  <a href="https://github.com/tfwljfans/weibo_task/issues">
        <img src="https://img.shields.io/github/issues/tfwljfans/weibo_task.svg"
             alt="GitHub issues">
  </a>
  <a href="https://github.com/tfwljfans/weibo_task/forks">
        <img src="https://img.shields.io/github/forks/tfwljfans/weibo_task.svg"
             alt="GitHub forks">
  </a>
  <a href="https://github.com//tfwljfans/weibo_task/">
        <img src="https://img.shields.io/github/last-commit/tfwljfans/weibo_task.svg">
  </a>
</p>

<h4 align="center">
    <p>一款通过微信小程序管理微博的小工具（后端微博相关接口）</p>
    <a href="https://github.com/tfwljfans/wx_miniprogram">一款通过微信小程序管理微博的小工具（前端页面）</a>
</h4>

## 项目梗概

- 本项目通过对微博接口的爬取，实现登录微博、上传图片、发送微博（主页/超话）、转发微博、点赞微博以及评论微博等功能。
- 本项目来源于“一款通过微信小程序管理微博的小工具”，目前仅提供微博相关接口

## 各接口说明

### 登录相关
<a href="#获取二维码URL">获取二维码URL</a></br>
<a href="#获取登录状态">获取登录状态</a></br>
<a href="#获取并持久化Cookie">获取并持久化Cookie</a></br>


#### 获取二维码URL
```python
sinaLogin.py

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
```
#### 获取登录状态
```python
sinaLogin.py

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
```
#### 获取并持久化Cookie
```python
sinaLogin.py

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
```

