# -*- coding: utf-8 -*-
from scrapy import cmdline
import os
import subprocess

def run_command(name, log):
    if log:
        command = 'scrapy crawl ' + name
    else:
        command = 'scrapy crawl ' + name + ' --nolog'
    env = os.environ.copy()
    process_ = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, env=env)
    return process_

def run_crawler(conn, log=False):
    trans = {}  # 用于记录进程和爬虫名字对应关系
    process_list = []
    failed_process = []  # 记录是错误的爬虫
    spider_name = ['fans']
    # 启动多个爬虫，同时在运行
    for name in spider_name:
        process = run_command(name, log)
        trans[process] = name
        process_list.append(process)
    while process_list:
        # print([trans[item] for item in process_list])
        for process in process_list:
            # 循环读取打印的内容
            output = process.stdout.readline()
            if output:
                content = output.decode('utf-8').strip()
                print(content)
                if '该套餐已过期' in content:
                    failed_process.append("爬虫 " + trans[process] + "的IP申请失败，请前往https://www.siyetian.com/apis.html"
                                                                   "手动获取最新api链接")  # 保存出错的爬虫名称
                elif '微博cookie已过期' in content:
                    failed_process.append("爬虫 " + trans[process] + "的微博cookie已过期，请前往https://weibo.com/u/page/follow"
                                                                   "/2719034460?relate=fans手动更新cookie")

    # 进程结束时将其移除进程列表
            if process.poll() is not None:
                process_list.remove(process)

if __name__ == "__main__":
    run_crawler(conn=None, log=False)
