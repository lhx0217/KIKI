# coding=utf-8
import http.client
import time
import urllib
from copyheaders import headers_raw_to_dict
from weibo import APIClient
import requests


class WeiBoInfo:
    def __init__(self, app_key, app_secret, callback_url, username, password):
        # 利用官方微博SDK
        self.client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback_url)
        # 在网站放置“使用微博账号登录”的链接，当用户点击链接后，引导用户跳转至如下地址：
        url = self.client.get_authorize_url()
        # callback url
        conn = http.client.HTTPSConnection('api.weibo.com')
        postdata = urllib.parse.urlencode(
            {'client_id': app_key, 'response_type': 'code', 'redirect_uri': callback_url, 'action': 'submit',
             'userId': username, 'passwd': password, 'isLoginSina': 0, 'from': '', 'regCallback': '', 'state': '',
             'ticket': '', 'withOfficalFlag': 0})
        # 直接复制浏览器的请求，删掉冒号
        headers = b'''authority: api.weibo.com
method: GET
path: /oauth2/authorize?client_id=2367684227&response_type=code&redirect_uri=https%3A%2F%2Fapi.weibo.com%2Foauth2%2Fdefault.html&action=submit&userId=%E7%94%A8%E6%88%B79876583554&passwd=qwe127227472&isLoginSina=0&from=&regCallback=&state=&ticket=&withOfficalFlag=0
scheme: https
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
cookie: SINAGLOBAL=854091521546.8892.1681147181385; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWYBr.gsLP6dXfcYWznKdh.5JpX5KMhUgL.FoMReo.fSo.pS022dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM41hMcSKn0SK-X; UOR=,,www.baidu.com; ULV=1682870959293:8:1:4:7947653765197.227.1682870959283:1682339011441; JSESSIONID=045EAB1B641D24DF3E41F5747EB7091A; ALF=1685551399; SSOLoginState=1682959400; SCF=AmvalvHGBo3cbUEZ0zYRzQDBfoS9f7yiuhkagWnVzHFqgJWvRE62PoQvviTfp8jBmobQ3iSsNB5yeWJrifC1DM4.; SUB=_2A25JS5x4DeRhGeFG6VsU9ifNzD2IHXVqIIqwrDV8PUNbmtANLUvxkW9NecuFqAYizu88IlnynK7klmmLEXw4heTy
pragma: no-cache
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="8"
sec-ch-ua-mobile: ?0
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/25'''
        # dic = headers_raw_to_dict(headers)
        # for n in dic.keys():
        #     print(n, ': ', dic[n])
        url = 'https://api.weibo.com/oauth2/authorize?' + postdata
        conn.request('GET', url, headers=headers_raw_to_dict(headers))
        res = conn.getresponse()
        location = res.getheader('Location')
        try:
            code = location.split('=')[1]
        except:
            raise ZeroDivisionError('请点击该网址修改cookies: https://api.weibo.com/oauth2/authorize?' + postdata)
        conn.close()
        print('自动获取的code：', code)
        r = self.client.request_access_token(code)
        access_token = r.access_token  # 新浪返回的token，类似abc123xyz456
        expires_in = r.expires_in
        # 设置得到的access_token
        self.client.set_access_token(access_token, expires_in)

    # 获取当前登录用户及其所关注用户的最新微博消息。和用户登录 http://t.sina.com.cn 后在“我的首页”中看到的内容相同。
    # 别名statuses/home_timeline
    def get_personal(self):
        """
        此时statuses为一个列表, 包含首页的20条消息, 每条信息是一个字典 字典的关键字: ['visible', 'created_at', 'id', 'idstr', 'mid', 'can_edit',
        'version', 'show_additional_indication', 'text', 'textLength', 'source_allowclick', 'source_type',
        'source', 'favorited', 'truncated', 'in_reply_to_status_id', 'in_reply_to_user_id',
        'in_reply_to_screen_name', 'pic_urls', 'thumbnail_pic', 'bmiddle_pic', 'original_pic', 'geo', 'is_paid',
        'mblog_vip_type', 'user', 'reposts_count', 'comments_count', 'reprint_cmt_count', 'attitudes_count',
        'pending_approval_count', 'isLongText', 'reward_exhibition_type', 'hide_flag', 'mlevel', 'show_mlevel',
        'biz_feature', 'page_type', 'hasActionTypeCard', 'darwin_tags', 'hot_page', 'hot_weibo_tags',
        'text_tag_tips', 'mblogtype', 'rid', 'userType', 'mlevelSource', 'more_info_type', 'cardid',
        'positive_recom_flag', 'enable_comment_guide', 'content_auth', 'gif_ids', 'is_show_bulletin',
        'comment_manage_info', 'pic_num', 'alchemy_params', 'can_reprint', 'new_comment_style', 'ab_switcher']
        """
        statuses = self.client.statuses__friends_timeline()['statuses']
        length = len(statuses)
        # 输出了部分信息
        for i in range(0, length):
            print(u'昵称：' + statuses[i]['user']['screen_name'])
            print(u'位置：' + statuses[i]['user']['location'])
            print(u'微博：' + statuses[i]['text'])

    def search_user(self, name=None, identity=None):
        # 获取用户信息
        try:
            if identity:
                result = self.client.users__show(uid=identity)
            else:
                result = self.client.users__show(screen_name=name)
            print(u'昵称：' + result['screen_name'])
            print(u'id: ' + str(result['id']))
            print(u'位置：' + result['location'])
            return str(result['id'])
        except:
            print("用户不存在")
            return "no specific user"
        # 获取粉丝信息
        # if identity:
        #     fans = self.client.friendships__followers(uid=identity)
        # else:
        #     fans = self.client.friendships__followers(screen_name=name)
        # print(len(fans))

    def test_relation(self, name1, name2):
        relation = self.client.friendships__show(source_screen_name=name1, target_screen_name=name2)
        if relation['source']['following'] and relation['source']['followed_by']:
            print("%s和%s互相关注")
        elif relation['source']['following']:
            print(name1, "关注了", name2)
        elif relation['source']['followed_by']:
            print(name2, "关注了", name1)
        else:
            print("%s和%s没有关注关系")


if __name__ == "__main__":
    APP_KEY = '2367684227'
    APP_SECRET = '11e1c50b8a129207598cf3b0fbcc0a38'
    CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
    USER_NAME = '用户9876583554'
    PASSWORD = 'qwe127227472'
    wb_info = WeiBoInfo(APP_KEY, APP_SECRET, CALLBACK_URL, USER_NAME, PASSWORD)
    # wb_info.get_personal()
    name = "summerwwxxyy"
    identy = 7808476910
    wb_info.search_user(name=name)
    # wb_info.test_relation('观察者网', '新浪新闻')
