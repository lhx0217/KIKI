# -*- coding: utf-8 -*-
import scrapy
import json
import time
import copy
from mySpider.items import UserItem, CommentItem, StatusesItem
from mySpider import settings
from mySpider import utils
from pyquery import PyQuery as pq
import threading

class WeiboSpider(scrapy.Spider):
    name = "fans"
    allowed_domains = ['weibo.com']
    total = []
    try:
        with open(settings.QUERY + '.txt', 'r', encoding='gbk') as f:
            exsist = f.readlines()
            for t in range(len(exsist)):
                exsist[t] = exsist[t][:-1]
                print(t, ': ', exsist[t])
    except Exception as err:
        print('err:', err)
        exsist = []
    count = 0  # 所有爬取是否结束

    def start_requests(self):
        """首先请求第一个js文件，包含有关注量，姓名等信息"""
        info_url = 'https://s.weibo.com/weibo?q=' + settings.QUERY + '&page='
        for i in range(80):
            yield scrapy.Request(url=info_url + str(i), callback=self.parse_comment_href)
        thd = threading.Thread(target=self.store, daemon=False)
        thd.start()

    def parse_comment_href(self, response):
        content = pq(response.text)
        # print(content.find('.content'))
        for t in content.find('.card-wrap'):
            if 'mid' not in t.attrib.keys():
                continue
            sid = t.attrib['mid']
            comment_url = "https://weibo.com/ajax/statuses/buildComments?id=" + sid + \
                          "&is_show_bulletin=2"
            yield scrapy.Request(url=comment_url, callback=self.parse_comment, meta={'sid': sid})
            self.count += 1


    def parse_comment(self, response):
        """想要加载全部评论, 规律为max_id字段不断迁移"""
        sid = response.meta['sid']
        content = json.loads(response.text)
        max_id = str(content['max_id'])
        comment_list = content['data']
        if not comment_list:
            self.count -= 1
            return
        for comment in comment_list:
            comment_info = CommentItem()
            comment_info = utils.gen_comment_info(comment_info, comment, sid)
            if comment_info['text'] not in self.exsist and comment_info['text'] not in self.total:
                self.total.append(comment_info['text'])
                print(comment_info['text'])
            for tx in comment_info['comment_comment']:
                if tx not in self.exsist and tx not in self.total:
                    self.total.append(tx)
                    print(tx)
            # yield comment_info
        next_page_url = "https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id=" + sid + \
                        "&is_show_bulletin=2&is_mix=0&max_id=" + max_id
        yield scrapy.Request(url=next_page_url, callback=self.parse_comment, meta={'sid': sid})

    def store(self):
        cnt = -1
        while self.count:
            if cnt == self.count:
                print('未输出')
                break
            print('现存线程: ', self.count)
            cnt = copy.deepcopy(self.count)
            time.sleep(10)

        with open(settings.QUERY + '.txt', 'a+', encoding='gbk') as fil:
            for t in self.total:
                try:
                    fil.write(t + '\n')
                except Exception as err:
                    print(err)
        print('存储完毕')
