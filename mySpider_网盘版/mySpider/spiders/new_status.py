import scrapy
import json
from mySpider.items import CommentItem, StatusesItem
from mySpider import settings
from mySpider import utils


class WeiboSpider_status(scrapy.Spider):
    name = "new_status"
    allowed_domains = ['weibo.com']
    statuses_url = "https://weibo.com/ajax/statuses/mymblog?uid=" + settings.ID + "&page="
    statuses_offset = 1
    sid = 0

    def start_requests(self):
        """首先请求第一个js文件，包含有关注量，姓名等信息"""
        statuses_url = 'https://weibo.com/ajax/statuses/mymblog?uid=' + settings.ID + '&page=1'
        print(statuses_url)
        yield scrapy.Request(url=statuses_url, callback=self.parse_statuses)

    def parse_statuses(self, response):
        content = json.loads(response.text)
        if 'data' not in content.keys():
            print('微博cookie已过期')
            raise SystemExit
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
            comment_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&id=" + self.sid + \
                          "&is_show_bulletin=2&is_mix=0&count=10"
            yield scrapy.Request(url=comment_url, callback=self.parse_comment)
        self.statuses_offset += 1
        statuses_url = self.statuses_url + str(self.statuses_offset)
        print("博文页码: ", self.statuses_offset)
        yield scrapy.Request(url=statuses_url, callback=self.parse_statuses)

    def parse_comment(self, response):
        """想要加载全部评论, 规律为max_id字段不断迁移"""
        content = json.loads(response.text)
        max_id = str(content['max_id'])
        comment_list = content['data']
        if not comment_list:
            return
        print('评论列表长度:', len(comment_list))
        for comment in comment_list:
            comment_info = CommentItem()
            comment_info = utils.gen_comment_info(comment_info, comment, self.sid)
            yield comment_info
        next_page_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id=" + self.sid + \
                        "&is_show_bulletin=2&is_mix=0&max_id=" + max_id
        if max_id != '0':
            print("评论的下一页id: ", max_id)
            yield scrapy.Request(url=next_page_url, callback=self.parse_comment)

