from abc import ABC

import scrapy
import json
from mySpider.items import UserItem, CommentItem, StatusesItem
from mySpider import settings
from mySpider import utils


class WeiboSpider(scrapy.Spider):
    name = "fans"
    allowed_domains = ['weibo.com']
    # 我的cookie和http请求, 需要定期更新
    flag = True
    fan_url = "https://weibo.com/ajax/friendships/friends?relate=fans&page="
    fan_offset = 1
    statuses_url = "https://weibo.com/ajax/statuses/mymblog?uid=" + settings.ID + "&page="
    statuses_offset = 1
    followed_offset = 1
    sid = 0

    def start_requests(self):
        """首先请求第一个js文件，包含有关注量，姓名等信息"""
        info_url = 'https://weibo.com/ajax/profile/info?uid=' + settings.ID
        yield scrapy.Request(url=info_url, callback=self.parse_user_info, meta={})

    def parse_user_info(self, response):
        content = json.loads(response.text)
        # 调用者是start则用settings, fans调用则用传入的ID
        if 'ID' in response.meta.keys():
            ID = str(response.meta['ID'])
        else:
            ID = settings.ID
        if not content["ok"]:
            print("==========user info error===========")
            return
        if 'data' not in content.keys():
            print('微博cookie已过期')
            raise SystemExit
        info = content['data']['user']
        user_item = UserItem()
        user_item = utils.gen_user_info(user_item, info)
        detail_url = "https://weibo.com/ajax/profile/detail?uid=" + ID
        # meta为parse_user_detail函数传参, 只有查询本人信息需要调用此函数
        meta = {'user_item': user_item, 'group': 0}
        yield scrapy.Request(url=detail_url, callback=self.parse_user_detail, meta=meta)

    def parse_user_detail(self, response):
        """接受一个meta参数{'user_item': None, 'group': None}"""
        user_item = response.meta['user_item']
        group = response.meta['group']
        content = json.loads(response.text)
        if not content["ok"]:
            print("==========user detail error===========")
            return
        detail = content['data']
        user_item = utils.gen_user_detail(user_item, detail)
        user_item['group'] = group
        yield user_item
        # flag的目的是确保只调用一次搜集粉丝信息函数parse_fans
        if self.flag:
            # 设置数据库名字
            settings.NAME = user_item['screen_name']
            # page是页码
            fans_url = "https://weibo.com/ajax/friendships/friends?relate=fans&page=1&uid=" + settings.ID
            self.flag = False
            print("========user yield into fans=========")
            yield scrapy.Request(url=fans_url, callback=self.parse_fans)

    def parse_fans(self, response):
        content = json.loads(response.text)
        # 是0代表已经无法访问到
        if 'users' not in content.keys():
            print("==========fans data error===========")
            if 'msg' in content.keys():
                print(content['msg'])
            # 用return结束yield继续执行
            return
        user_list = content["users"]
        if not user_list:
            print("==========粉丝遍历完成===========")
            print("其内容为：")
            print(response.text)
            print("=" * 28)
            # 收集完粉丝信息后继续搜集博文信息
            statuses_url = 'https://weibo.com/ajax/statuses/mymblog?uid=' + settings.ID + '&page=1'
            print(statuses_url)
            yield scrapy.Request(url=statuses_url, callback=self.parse_statuses)
            return

        for user in user_list:
            user_info = UserItem()
            user_info = utils.gen_user_info(user_info, user)
            user_info = utils.gen_user_detail(user_info, user)
            # 详细查询每个用户信息会导致414，IP地址被服务器限制访问
            info_url = "https://weibo.com/ajax/profile/detail?uid=" + str(user_info['uid'])
            yield scrapy.Request(url=info_url, callback=self.parse_user_detail,
                                 meta={'user_item': user_info, 'group': 1})
            # user_info['group'] = 1
            # yield user_info
        # 翻页遍历所有的粉丝信息
        self.fan_offset += 1
        fans_url = self.fan_url + str(self.fan_offset) + "&uid=" + settings.ID
        print("页码: ", self.fan_offset)
        yield scrapy.Request(url=fans_url, callback=self.parse_fans)

    def parse_statuses(self, response):
        content = json.loads(response.text)
        statuses_list = content['data']['list']
        if not statuses_list:
            print("==========博文遍历完成===========")
            return
        for statuses in statuses_list:
            statuses_info = StatusesItem()
            statuses_info = utils.gen_statuses_info(statuses_info, statuses)
            yield statuses_info
            self.sid = statuses_info['sid']
            # is_show_bulletin: 1为按时间排序, 2为按热度排序
            comment_url = "https://weibo.com/ajax/statuses/buildComments?id=" + self.sid + \
                          "&is_show_bulletin=2"
            yield scrapy.Request(url=comment_url, callback=self.parse_comment)
        self.statuses_offset += 1
        statuses_url = self.statuses_url + str(self.statuses_offset)
        print("页码: ", self.statuses_offset)
        yield scrapy.Request(url=statuses_url, callback=self.parse_statuses)

    def parse_comment(self, response):
        """想要加载全部评论, 规律为max_id字段不断迁移"""
        content = json.loads(response.text)
        max_id = str(content['max_id'])
        comment_list = content['data']
        if not comment_list:
            print("==========评论遍历完成===========")
            followed_page_url = "https://weibo.com/ajax/friendships/friends?page=" + str(self.followed_offset) \
                                + "&uid=" + settings.ID
            yield scrapy.Request(url=followed_page_url, callback=self.parse_followed)
            return
        for comment in comment_list:
            comment_info = CommentItem()
            comment_info = utils.gen_comment_info(comment_info, comment, self.sid)
            yield comment_info
        next_page_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id=" + self.sid + \
                        "&is_show_bulletin=2&is_mix=0&max_id=" + max_id
        print("最大id: ", max_id)
        yield scrapy.Request(url=next_page_url, callback=self.parse_comment)

    def parse_followed(self, response):
        """关注列表"""
        content = json.loads(response.text)
        followed_list = content['users']
        if not followed_list:
            print("==========关注者遍历完成===========")
            return
        for user in followed_list:
            user_info = UserItem()
            user_info = utils.gen_user_info(user_info, user)
            user_info = utils.gen_user_detail(user_info, user)
            info_url = "https://weibo.com/ajax/profile/detail?uid=" + str(user_info['uid'])
            yield scrapy.Request(url=info_url, callback=self.parse_user_detail, meta={'user_item': user_info, 'group': 2})
            # user_info['group'] = 2
            # yield user_info
        print('关注者列表序号: ', self.followed_offset)
        self.followed_offset += 1
        followed_page_url = "https://weibo.com/ajax/friendships/friends?page=" + str(self.followed_offset) \
                            + "&uid=" + settings.ID
        yield scrapy.Request(url=followed_page_url, callback=self.parse_followed)
