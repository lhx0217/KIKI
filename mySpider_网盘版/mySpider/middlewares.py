# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
from mySpider import utils
from scrapy import signals
import random
from mySpider.代理IP import *

def ip_list(num):
    proxies_list = []
    typ = "free"
    while num > 0:
        time.sleep(1)
        ip = get_ip(typ)
        if ip == "code:10019":
            typ = "paid"
            print("free ip已达最大使用次数")
        elif "code" not in ip:
            proxies_list.append(ip)
            print(typ + ' ip使用成功')
            print('申请到的ip为: ', ip)
            num -= 1
        elif ip == "code:10005":
            print('该套餐已过期')
            raise SystemExit
    return proxies_list

class RequestMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    # 浏览器池
    user_agents = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
    ]
    # cookie池
    cookies = [r'XSRF-TOKEN=iQuZb_Yp26cQMAHIgGRfTSYC; SSOLoginState=1690295313; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWYBr.gsLP6dXfcYWznKdh.5JpX5KMhUgL.FoMReo.fSo.pS022dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM41hMcSKn0SK-X; ALF=1693147793; SCF=Ass088_dBkf7MzdekwWlt5rLCl-BYpNLrYOlfBCDFZrkf2P-Tm3--h26s1Y_b7xJBgR3ymLF14AU8DSgduZ3Zd0.; SUB=_2A25Jx6XDDeRhGeFG6VsU9ifNzD2IHXVqtJALrDV8PUNbmtAGLXbkkW9NecuFqG88idj6f98stieTglfCnheRdFCf; WBPSESS=cr4hkwwxfJb_HtFDhT8YoC0YE2NMcVda9jxGBXyZ-_yynmx6OMB8iwfN-2h3slSTXyJj6fGYHIt8_nXUwczOPyt18pvcnWa464OOht2UgA9QuU906PaVD8BivpJEyioAzNnTnRQCvHvB0WcU4N7tZQ==']

    proxies_list = ip_list(1)
    print('代理IP列表:', proxies_list)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        request.headers['User-Agent'] = random.choice(self.user_agents)
        request.cookies = utils.operate_cookies(random.choice(self.cookies))
        # 是proxy一定是要写成 http:// 前缀，否则会出现to_bytes must receive a unicode, str or bytes object, got NoneType的错误
        choose = random.randint(0, 10)
        if choose > 3:
            request.meta['proxy'] = "http://" + random.choice(self.proxies_list)
        else:
            request.meta['proxy'] = ''
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # 处理失效代理IP
        print('发生错误：', exception)
        print('代理IP ' + request.meta["proxy"] + '已失效')
        try:
            self.proxies_list.remove(request.meta["proxy"].split('//')[1])
            self.proxies_list += ip_list(1)
            print('现存代理IP池：', self.proxies_list)
        except Exception as err:
            print(err)


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
