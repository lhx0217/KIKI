from abc import ABC

import scrapy
import json
from mySpider.items import UserItem, CommentItem, StatusesItem
from mySpider import settings
from mySpider import utils


class WeiboSpider_followed(scrapy.Spider):
    name = "new_followed"
    allowed_domains = ['weibo.com']
    followed_offset = 1
    sid = 0

    def start_requests(self):
        """首先请求第一个js文件，包含有关注量，姓名等信息"""
        followed_page_url = "https://weibo.com/ajax/friendships/friends?page=" + str(self.followed_offset) \
                            + "&uid=" + settings.ID
        yield scrapy.Request(url=followed_page_url, callback=self.parse_followed)

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
        print('当前关注的人昵称: ', user_item['screen_name'])
        yield user_item

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
        print('关注者列表序号: ', self.followed_offset)
        self.followed_offset += 1
        followed_page_url = "https://weibo.com/ajax/friendships/friends?page=" + str(self.followed_offset) \
                            + "&uid=" + settings.ID
        yield scrapy.Request(url=followed_page_url, callback=self.parse_followed)
