import hashlib
import json
import os
import re
import time
from urllib import parse
# from proxy.proxyMain import proxy
from Dao.proxyDao import Dao
# import execjs
import requests

requests.packages.urllib3.disable_warnings()


class Weibo(object):
    def __init__(self, cookie, headers, sess, nickName, uid, post_delay):
        """
        微博任务类，包括执行各种任务

        :param cookie: 用户cookie
        :param headers: 用户headers
        :param sess: 用户保留的sess
        :param nickName: 用户昵称
        :param uid: 用户uid
        :param post_delay: 发送延迟
        """
        self.cookie = cookie
        self.headers = headers
        self.post_delay = post_delay
        self.sess = sess
        # self.sess = requests
        self.nickName = nickName[0]
        self.uid = int(uid[0])
        self.dao = Dao()
        self.proxyConfig = json.loads(
            open(os.getcwd() + "/proxy/proxyConfig.json", encoding="utf-8").read()) # 动态IP
        self.authKey = self.proxyConfig["authKey"] # 动态IP池的key
        self.password = self.proxyConfig["password"] # 动态IP池的password
        self.timeout = 5
        self.timeoutReq = 10
        self.timeoutPic = 20
        self.config = json.loads(
            open("/".join(os.getcwd().split("/")[:-1]) + "/config.json", encoding="utf-8").read())
        # print(self.nickName)
        # print(self.uid)



    def post_SuperTopicWeiboCustom(self, text, pdetail, pic=[""]):
        """
        将微博发送至超话

        :param text: 文案内容
        :param pdetail: 超话ID
        :param pic: 是否包含图片，列表内容为上传的图片ID
        :return: 发送成功True / 发送失败False
        """
        url = "https://weibo.com/p/aj/proxy?ajwvr=6&__rnd=" + str(int(time.time() * 1000))

        picStr = "|".join(pic)

        data = {"location": "page_100808_super_index", "text": text, "appkey": "", "style_type": 1,
                "pic_id": picStr, "tid": "", "pdetail": pdetail, "mid": "",
                "isReEdit": "false", "gif_ids": "", "sync_wb": 1, "pub_source": "page_1",
                "api": "http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id=" + pdetail,
                "object_id": "1022:" + pdetail, "module": "publish_913",
                "page_module_id": 913, "longtext": 1, "topic_id": "1022:" + pdetail,
                "updata_img_num": 1, "pub_type": "dialog", "_t": 0}
        Header = self.headers
        Header["Host"] = "weibo.com"
        Header["Referer"] = "https://weibo.com/p/" + pdetail + "/super_index"
        proxies = self._getProxy()
        # root_path = "/".join(os.getcwd().split("/")[:-1])
        root_path = os.getcwd()
        try:
            response = self.sess.post(url=url, data=data, headers=Header, verify=False, proxies=proxies,
                                      timeout=self.timeout)
        except Exception as e:
            try:
                response = self.sess.post(url=url, data=data, headers=Header, verify=False, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("post_SuperTopicWeiboCustom->", response.text)

        try:
            response = response.json()
            code = response["code"]
            if not isinstance(code, str):
                return False
        except Exception as e:
            return False

        if code == "100000":
            time.sleep(self.post_delay)
            return True
        return False

    def post_SuperTopicWeibo(self, topics, emotes, copyWriting, pic=[""], video_url=[""]):
        """
        description: 发送微博的基础函数
        param str text 微博文字内容
        param str intime 定时微博发布时间的时间戳（毫秒）
        param str pic 微博图片id，以逗号分隔
        param int rank 可以查看微博的人 1仅自己 0公开 6好友圈 10粉丝
        return dict response 微博返回数据
        """

        url = "https://weibo.com/p/aj/proxy?ajwvr=6&__rnd=" + str(int(time.time() * 1000))

        text = '#王橹杰[超话]# ' + emotes[0] + topics[0] + emotes[1] + topics[1] + '\n\n ' \
               + copyWriting[-1] + '\n\n' + '@TF家族-王橹杰LJW ' + '\n\n' + video_url[0]

        picStr = "|".join(pic)

        data = {"location": "page_100808_super_index", "text": text, "appkey": "", "style_type": 1,
                "pic_id": picStr, "tid": "", "pdetail": "1008080587fa0e8198ad45108f3a0ef6e08d3a", "mid": "",
                "isReEdit": "false", "gif_ids": "", "sync_wb": 1, "pub_source": "page_1",
                "api": "http://i.huati.weibo.com/pcpage/operation/publisher/sendcontent?sign=super&page_id"
                       "=1008080587fa0e8198ad45108f3a0ef6e08d3a",
                "object_id": "1022:1008080587fa0e8198ad45108f3a0ef6e08d3a", "module": "publish_913",
                "page_module_id": 913, "longtext": 1, "topic_id": "1022:1008080587fa0e8198ad45108f3a0ef6e08d3a",
                "updata_img_num": 1, "pub_type": "dialog", "_t": 0}

        # print("postMain->", data)
        # print("picStr->", picStr)

        Header = self.headers
        Header["Host"] = "weibo.com"
        Header["Referer"] = "https://weibo.com/p/1008080587fa0e8198ad45108f3a0ef6e08d3a/super_index"
        proxies = self._getProxy()
        # root_path = "/".join(os.getcwd().split("/")[:-1])
        root_path = os.getcwd()
        try:
            response = self.sess.post(url=url, data=data, headers=Header, verify=False, proxies=proxies,
                                      timeout=self.timeout)
        except Exception as e:
            try:
                response = self.sess.post(url=url, data=data, headers=Header, verify=False, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("post_SuperTopicWeibo->", response.text)

        try:
            response = response.json()
            code = response["code"]
            if not isinstance(code, str):
                return False
        except Exception as e:
            return False

        if code == "100000":
            time.sleep(self.post_delay)
            return True
        return False

    def setLike_SuperTopicWeibo(self, bid):
        """
        点赞微博

        :param bid: 点赞微博id
        :return:
        """

        data = {
            "location": "page_100808_super_index",
            "filiter_actionlog": "",
            "version": "mini",
            "qid": "heart",
            "mid": bid,
            "loc": "page_102803_home",
            "cuslike": 1,
            "hide_mult_attitude": 1,
            "floating": 0,
            "_t": 0
        }

        url = "https://weibo.com/aj/v6/like/add?ajwvr=6&__rnd=" + str(int(time.time() * 1000))
        Header = self.headers
        Header["Referer"] = "https://weibo.com/p/1008080587fa0e8198ad45108f3a0ef6e08d3a/super_index"
        proxies = self._getProxy()
        try:
            resp = self.sess.post(url, data=data, headers=Header, proxies=proxies, timeout=self.timeout)
        except Exception as e:
            try:
                resp = self.sess.post(url, data=data, headers=Header, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("setLike_SuperTopicWeibo->", resp.text)
        try:
            resp = resp.json()
            code = resp["code"]
            if not isinstance(code, str):
                return False
        except Exception as e:
            return False

        if code == "100000":
            time.sleep(self.post_delay)
            return True
        return False

    def comment_SuperTopicWeibo(self, bid, uid, text):
        """
        评论微博

        :param bid: 评论微博ID
        :param uid: 评论用户ID
        :param text: 评论内容
        :return: 是否成功
        """
        """ post """
        url = "https://weibo.com/aj/v6/comment/add?ajwvr=6&__rnd=" + str(int(time.time() * 1000))

        data = {
            "act": "post",
            "mid": bid,
            "uid": uid,  # 2483943707 uid
            "forward": 0,
            "isroot": 0,
            "content": text,
            "location": "page_100808_super_index",
            "module": "scommlist",
            "group_source": "",
            "filter_actionlog": "",
            "pdetail": "1008080587fa0e8198ad45108f3a0ef6e08d3a",
            "_t": 0
        }
        Header = self.headers
        Header["Referer"] = "https://weibo.com/p/1008080587fa0e8198ad45108f3a0ef6e08d3a/super_index"
        proxies = self._getProxy()
        try:
            resp = self.sess.post(url, data=data, headers=Header, proxies=proxies, timeout=self.timeout)
        except Exception as e:
            try:
                resp = self.sess.post(url, data=data, headers=Header, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("comment_SuperTopicWeibo->", resp.text)
        try:
            resp = resp.json()
            code = resp["code"]
            if not isinstance(code, str):
                return False
        except  Exception as e:
            return False

        if code == "100000":
            time.sleep(self.post_delay)
            return True
        return False

    def repost_SuperTopicWeibo(self, bid, text):
        """
        转发微博

        :param bid: 被转发微博ID
        :param text: 转发时的内容
        :return:
        """
        url = "https://weibo.com/aj/v6/mblog/forward?ajwvr=6&domain=100808&__rnd=" + str(int(time.time() * 1000))

        data = {
            "pic_src": "",
            "pic_id": "",
            "appkey": "",
            "mid": bid,
            "style_type": 1,
            "mark": "",
            "reason": text,
            "location": "page_100808_super_index",
            "pdetail": "1008080587fa0e8198ad45108f3a0ef6e08d3a",
            "module": "",
            "page_module_id": "",
            "refer_sort": "",
            "rank": 0,
            "rankid": "",
            "filter_actionlog": "",
            "isReEdit": "false",
            "_t": 0,
        }
        Header = self.headers
        Header["Referer"] = "https://weibo.com/p/1008080587fa0e8198ad45108f3a0ef6e08d3a/super_index"
        proxies = self._getProxy()
        try:
            resp = self.sess.post(url, data=data, headers=Header, proxies=proxies, timeout=self.timeout)
        except Exception as e:
            try:
                resp = self.sess.post(url, data=data, headers=Header, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("repost_SuperTopicWeibo->", resp.text)
        try:
            resp = resp.json()
            code = resp["code"]
            if not isinstance(code, str):
                return False
        except Exception as e:
            return False

        if code == "100000":
            time.sleep(self.post_delay)
            return True
        return False

    def upload_superTopicPic(self, paths):
        """
        description: 上传图片，获取id
        param list.str paths 待发送图片地址，支持网络图片（包括http头的）与本地图片
            例如：["https://www.baidu.com/bd.png","F:/desktop/b107.png"]
        return str 图片id字符串
        """
        pid = []
        for path in paths:
            p = None
            if "http" in path.lower():
                try:
                    file = requests.get(path).content
                    p = self._get_PicId(file)
                except requests.RequestException:
                    pass
            else:
                try:
                    with open(path, 'rb') as f:
                        p = self._get_PicId(f)
                except IOError:
                    pass
            if p:
                pid.append(p)

        if pid:
            return pid
        else:
            return None

    def post_MainWeibo(self, text, pic):
        """
        发送微博至主页

        :param text: 文案内容
        :param pic: 图片列表
        :return:
        """
        url = "https://weibo.com/ajax/statuses/update"

        data = {
            "content": text,
            "visible": 0,
            "share_id": "",
            # "pic_id": "",
            "media": "",
            "vote": "",
            # "approval_state": 0
        }

        if pic != None and len(pic) != 0:
            # pics = []
            # for p in pic:
            #     tmp = {
            #         "type": "image/jpeg",
            #         "pid": p
            #     }
            #     pics.append(tmp)
            pics = ",".join(pic)
            # # for p in pic:
            # #     pics += " " + p

            data["pic_id"] = pics.strip()

        # print("postMain->", data)
        Header = self.headers
        Header["Host"] = "weibo.com"
        Header["Referer"] = "https://weibo.com/"
        Header["X-Xsrf-Token"] = re.findall(r'XSRF-TOKEN=([^;]+)', self.cookie)[0]
        Header["Server-Version"] = "v2024.02.02.4"
        Header["Client-Version"] = "v2.44.62"
        Header["Accept-Encoding"] = "gzip, deflate, br"
        proxies = self._getProxy()
        try:
            response = self.sess.post(url=url, data=data, headers=Header, proxies=proxies, timeout=self.timeout)
        except Exception as e:
            try:
                response = self.sess.post(url=url, data=data, headers=Header, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("post_MainWeibo->", response.text)
        try:
            response = response.json()
            code = response["msg"]
            if not isinstance(code, str):
                return False
        except Exception as e:
            return False

        if code == "发布成功":
            time.sleep(self.post_delay)
            return True
        return False

    def upload_MainPic(self, pic):
        """
        上传图片

        :param pic: 图片路径
        :return: 图片ID
        """
        pids = []
        for p in pic:
            pic_md5, img = self._getMd5(p)
            pic_cs = self._getCs(img)
            pic_size = os.path.getsize(p)

            data = {
                "file_source": 1,
                "cs": pic_cs,
                "ent": "miniblog",
                "appid": 339644097,
                "uid": self.uid,
                "raw_md5": pic_md5,
                "ori": 1,
                "mpos": 1,
                "nick": self.nickName,
                "pri": 0,
                "request_id": str(int(time.time() * 1000)),
                "file_size": pic_size
            }
            dataUrl = parse.urlencode(data)
            Upload_API = "https://picupload.weibo.com/interface/upload.php?{}".format(dataUrl)
            data_pic = open(p, 'rb')
            Header = self.headers
            Header["Host"] = "picupload.weibo.com"
            Header["Accept"] = "application/json, text/plain, */*"
            Header["Sec-Fetch-Site"] = "same-site"
            proxies = self._getProxy()
            try:
                try:
                    response = self.sess.post(url=Upload_API, data=data_pic, headers=Header, proxies=proxies, timeout=self.timeoutPic).json()
                except Exception as e:
                    response = self.sess.post(url=Upload_API, data=data_pic, headers=Header, timeout=self.timeoutPic).json()
                pids.append(response["pic"]["pid"])
                time.sleep(self.post_delay)
            except Exception as e:
                return None
        return pids

    def checkRepost_MainWeibo(self, bid):
        """
        查看被转发微博是否可见，同时获取 被转发微博中的文案，之后将其添加至用户自定义文案后面

        :param bid: 被转发微博ID
        :return: 是否成功
        """
        mbid = self._mid_to_url(bid)
        proxies = self._getProxy()
        try:
            resp = self.sess.get("https://weibo.com/ajax/statuses/show?id={}&locale=zh-CN".format(mbid),
                                 headers=self.headers, proxies=proxies, timeout=self.timeout).json()
        except Exception as e:
            try:
                resp = self.sess.get("https://weibo.com/ajax/statuses/show?id={}&locale=zh-CN".format(mbid),
                                     headers=self.headers, timeout=self.timeoutReq).json()
            except:
                return False, False
        try:
            repostUser = resp["user"]["screen_name"]
            repostContext = resp["text_raw"]
        except:
            return False, False

        condition = self.config["repostCondition"]
        print("转发条件->", condition, type(condition), len(condition))
        if len(condition) == 0:
            return True, True
        else:
            for word in condition:
                if word in repostUser or word in repostContext:
                    return True, True
        return True, False

    def repost_MainWeibo(self, bid, comment):
        """
        转发微博

        :param bid: 被转发微博ID
        :param comment: 转发时的文案
        :return:
        """

        mbid = self._mid_to_url(bid)
        proxies = self._getProxy()
        try:
            resp = self.sess.get("https://weibo.com/ajax/statuses/show?id={}&locale=zh-CN".format(mbid),
                                 headers=self.headers, proxies=proxies, timeout=self.timeout).json()
        except Exception as e:
            try:
                resp = self.sess.get("https://weibo.com/ajax/statuses/show?id={}&locale=zh-CN".format(mbid),
                                     headers=self.headers, timeout=self.timeoutReq).json()
            except:
                return False

        try:
            repostUser = resp["user"]["screen_name"]
            repostContext = resp["text_raw"]
        except:
            return False
        text = "//@" + repostUser + ":" + repostContext  # 将被转发微博的文案，添加到自定义文案后面
        comment = comment + text
        comment = comment[:140]

        repost_url = "https://weibo.com/ajax/statuses/normal_repost"
        data = {
            "id": bid,
            "comment": comment,
            "pic_id": "",
            "is_repost": 0,
            "comment_ori": 0,
            "is_comment": 0,
            "visible": 0,
            "share_id": ""
        }

        Header = self.headers
        Header["X-Xsrf-Token"] = re.findall(r'XSRF-TOKEN=([^;]+)', self.cookie)[0]
        try:
            resp = self.sess.post(repost_url, data=data, headers=Header, proxies=proxies, timeout=self.timeout)
        except Exception as e:
            try:
                resp = self.sess.post(repost_url, data=data, headers=Header, timeout=self.timeoutReq)
            except Exception as e:
                return False

        # print("repost_MainWeibo->", resp.text)
        try:
            resp = resp.json()
            msg = resp["msg"]
            if not isinstance(msg, str):
                return False
        except Exception as e:
            return False

        if msg == "转发成功":
            time.sleep(self.post_delay)
            return True
        return False

    def _getProxy(self):
        """
        获取动态IP

        :return: 代理
        """
        proxyAddr = self.dao.getProxy()
        proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
            "user": self.authKey,
            "password": self.password,
            "server": proxyAddr,
        }
        proxies = {
            "http": proxyUrl,
            "https": proxyUrl,
        }
        return proxies

    def _get_PicId(self, file):
        """
        description: 上传图片到微博，非新版微博使用接口
        param bytes-like file 待上传图片数据
        return str pid 微博图片id
        """
        Data = {
            'data': 1,
            'p': 1,
            'url': "weibo.com/u/{}".format(self.uid),
            'markpos': 1,
            'nick': '@{}'.format(self.nickName),
            'marks': 0,
            'app': 'miniblog',
            's': 'json',
            'pri': 'null',
            'file_source': 1
        }
        DataUrl = parse.urlencode(Data)
        Upload_API = "https://picupload.weibo.com/interface/pic_upload.php?{}".format(DataUrl)
        data = file
        Header = self.headers
        Header["Host"] = "picupload.weibo.com"
        proxies = self._getProxy()
        try:
            try:
                response = self.sess.post(url=Upload_API, data=data, headers=Header, proxies=proxies, timeout=self.timeoutPic).json()
            except Exception as e:
                response = self.sess.post(url=Upload_API, data=data, headers=Header, timeout=self.timeoutPic).json()
        except:
            return None

        if response["code"] == "A00006":
            pid = response["data"]["pics"]["pic_1"]["pid"]
            return pid
        time.sleep(self.post_delay)

    def _cal(self, l, le):
        a = -1
        for o in le:
            a = a % 0x100000000 >> 8 ^ l[255 & (a ^ o)]
        return (a ^ -1) % 0x100000000 >> 0

    def _getCs(self, pic_data):
        e = "00000000 77073096 EE0E612C 990951BA 076DC419 706AF48F E963A535 9E6495A3 0EDB8832 79DCB8A4 E0D5E91E 97D2D988 09B64C2B 7EB17CBD E7B82D07 90BF1D91 1DB71064 6AB020F2 F3B97148 84BE41DE 1ADAD47D 6DDDE4EB F4D4B551 83D385C7 136C9856 646BA8C0 FD62F97A 8A65C9EC 14015C4F 63066CD9 FA0F3D63 8D080DF5 3B6E20C8 4C69105E D56041E4 A2677172 3C03E4D1 4B04D447 D20D85FD A50AB56B 35B5A8FA 42B2986C DBBBC9D6 ACBCF940 32D86CE3 45DF5C75 DCD60DCF ABD13D59 26D930AC 51DE003A C8D75180 BFD06116 21B4F4B5 56B3C423 CFBA9599 B8BDA50F 2802B89E 5F058808 C60CD9B2 B10BE924 2F6F7C87 58684C11 C1611DAB B6662D3D 76DC4190 01DB7106 98D220BC EFD5102A 71B18589 06B6B51F 9FBFE4A5 E8B8D433 7807C9A2 0F00F934 9609A88E E10E9818 7F6A0DBB 086D3D2D 91646C97 E6635C01 6B6B51F4 1C6C6162 856530D8 F262004E 6C0695ED 1B01A57B 8208F4C1 F50FC457 65B0D9C6 12B7E950 8BBEB8EA FCB9887C 62DD1DDF 15DA2D49 8CD37CF3 FBD44C65 4DB26158 3AB551CE A3BC0074 D4BB30E2 4ADFA541 3DD895D7 A4D1C46D D3D6F4FB 4369E96A 346ED9FC AD678846 DA60B8D0 44042D73 33031DE5 AA0A4C5F DD0D7CC9 5005713C 270241AA BE0B1010 C90C2086 5768B525 206F85B3 B966D409 CE61E49F 5EDEF90E 29D9C998 B0D09822 C7D7A8B4 59B33D17 2EB40D81 B7BD5C3B C0BA6CAD EDB88320 9ABFB3B6 03B6E20C 74B1D29A EAD54739 9DD277AF 04DB2615 73DC1683 E3630B12 94643B84 0D6D6A3E 7A6A5AA8 E40ECF0B 9309FF9D 0A00AE27 7D079EB1 F00F9344 8708A3D2 1E01F268 6906C2FE F762575D 806567CB 196C3671 6E6B06E7 FED41B76 89D32BE0 10DA7A5A 67DD4ACC F9B9DF6F 8EBEEFF9 17B7BE43 60B08ED5 D6D6A3E8 A1D1937E 38D8C2C4 4FDFF252 D1BB67F1 A6BC5767 3FB506DD 48B2364B D80D2BDA AF0A1B4C 36034AF6 41047A60 DF60EFC3 A867DF55 316E8EEF 4669BE79 CB61B38C BC66831A 256FD2A0 5268E236 CC0C7795 BB0B4703 220216B9 5505262F C5BA3BBE B2BD0B28 2BB45A92 5CB36A04 C2D7FFA7 B5D0CF31 2CD99E8B 5BDEAE1D 9B64C2B0 EC63F226 756AA39C 026D930A 9C0906A9 EB0E363F 72076785 05005713 95BF4A82 E2B87A14 7BB12BAE 0CB61B38 92D28E9B E5D5BE0D 7CDCEFB7 0BDBDF21 86D3D2D4 F1D4E242 68DDB3F8 1FDA836E 81BE16CD F6B9265B 6FB077E1 18B74777 88085AE6 FF0F6A70 66063BCA 11010B5C 8F659EFF F862AE69 616BFFD3 166CCF45 A00AE278 D70DD2EE 4E048354 3903B3C2 A7672661 D06016F7 4969474D 3E6E77DB AED16A4A D9D65ADC 40DF0B66 37D83BF0 A9BCAE53 DEBB9EC5 47B2CF7F 30B5FFE9 BDBDF21C CABAC28A 53B39330 24B4A3A6 BAD03605 CDD70693 54DE5729 23D967BF B3667A2E C4614AB8 5D681B02 2A6F2B94 B40BBE37 C30C8EA1 5A05DF1B 2D02EF8D"
        arr = e.split(' ')
        new_arr = [int(i, 16) for i in arr]
        le = [i for i in pic_data]
        # js = execjs.compile("""
        # function cal(l,le){
        #     for ( var a=-1,i=l,o = 0, n =le.length; o < n; o++)
        #         a = a >>> 8 ^ i[255 & (a ^ le[o])];
        #     return (-1 ^ a) >>> 0
        #     }
        # """)
        # return js.call('cal', new_arr, le)
        res = self._cal(new_arr, le)
        return res

    def _getMd5(self, pic):
        fd = open(pic, "rb")
        img = fd.read()
        pmd5 = hashlib.md5(img)
        pic_md5 = pmd5.hexdigest()
        fd.close()
        return pic_md5, img

    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def _base62_encode(self, num, alphabet=ALPHABET):
        """Encode a number in Base X
        `num`: The number to encode
        `alphabet`: The alphabet to use for encoding
        """
        if (num == 0):
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            rem = num % base
            num = num // base
            arr.append(alphabet[rem])
        arr.reverse()
        return ''.join(arr)

    def _mid_to_url(self, midint):

        midint = str(midint)[::-1]
        size = len(midint) / 7 if len(midint) % 7 == 0 else len(midint) / 7 + 1
        size = int(size)
        result = []
        for i in range(size):
            s = midint[i * 7: (i + 1) * 7][::-1]
            s = self._base62_encode(int(s))
            s_len = len(s)
            if i < size - 1 and len(s) < 4:
                s = '0' * (4 - s_len) + s
            result.append(s)
        result.reverse()
        return ''.join(result)