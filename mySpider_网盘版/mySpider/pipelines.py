import pymysql
from mySpider import settings
from mySpider.items import UserItem, CommentItem, StatusesItem
import sys

class MyspiderPipeline:
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            use_unicode=True)
        self.cursor = self.connect.cursor()
        self.info_flag = {'微博': False, '评论': False}  # and的关系

    def create_user_table(self, group, item, spider):
        """用于新建存储用户的数据库表单, group为[‘_粉丝’, '', '_关注']"""
        # 选择sina数据库
        self.cursor.execute("use sina")
        # 获取所有表单
        self.cursor.execute("show tables")
        tables = self.cursor.fetchall()
        table_list = [t[0] for t in tables]
        name = settings.NAME.lower()
        if name + group not in table_list:
            print("名字(粉丝表单)：", name)
            # 需要设置主键
            sql = 'CREATE TABLE ' + name + group + \
                  ' (uid VARCHAR(255) PRIMARY KEY, 昵称 VARCHAR(255), 真实姓名 VARCHAR(255), 所在地 VARCHAR(255), 性别 VARCHAR(255), ' \
                  '生日 VARCHAR(255), QQ VARCHAR(255), 简介 VARCHAR(255), 粉丝数 VARCHAR(255), 关注数 VARCHAR(255),  ' \
                  '微博数 VARCHAR(255), 微博认证用户 VARCHAR(255), 注册时间 VARCHAR(255), 微博会员等级 ' \
                  'VARCHAR(255), 职业信息 VARCHAR(255), 教育信息 VARCHAR(255), 标签 VARCHAR(255), 信誉 VARCHAR(255), ' \
                  'ip属地 VARCHAR(255));'
            self.cursor.execute(sql)
        else:
            pass

        insert = 'insert ignore into ' + name + group + \
                 ' (uid, 昵称, 真实姓名, 所在地, 性别, 生日, QQ, 简介, 粉丝数, 关注数, 微博数, 微博认证用户, 注册时间, 微博会员等级' \
                 ', 职业信息, 教育信息, 标签, 信誉, ip属地) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,' \
                 '%s); '
        self.cursor.execute(insert,
                            [item['uid'], item['screen_name'], item['real_name'], item['location'],
                             item['gender'],
                             item['birthday'], item['qq'], item['description'],
                             item['followers_count'], item['follow_count'], item['statuses_count'],
                             item['verified'], item['regist_time'], item['mbrank'], item['profession'],
                             item['education'], item['lable'], item['credit'], item['ip_location']])
        self.connect.commit()  # 这行太重要啦！！！！查了我半个小时

    def process_item(self, item, spider):
        dic = {0: '', 1: '_粉丝', 2: '_关注'}
        # 传来的是User对象
        if isinstance(item, UserItem):
            group = item['group']
            self.create_user_table(dic[group], item, spider)
        # 传来的是Status对象
        if isinstance(item, StatusesItem):
            self.cursor.execute("use sina")
            self.cursor.execute("show tables")
            tables = self.cursor.fetchall()
            table_list = [t[0] for t in tables]
            name = settings.NAME.lower()
            if name + '_微博' not in table_list:
                print("名字(博文表单)：", name)
                sql = 'CREATE TABLE ' + name + '_微博 ' + \
                      '(sid VARCHAR(255) PRIMARY KEY, 创建时间 VARCHAR(255), 文本 VARCHAR(1024), 发送设备 VARCHAR(255), ' \
                      '阅读数 VARCHAR(255), 转发数 VARCHAR(255), 评论数 VARCHAR(255), 点赞数 VARCHAR(255),  ' \
                      '话题 VARCHAR(255), 发布于 VARCHAR(255));'  # 此处写的时候少了一个括号检查了好久
                self.cursor.execute(sql)
            else:
                pass
            # 如果两个都为True则终止程序
            if self.info_flag['微博'] and self.info_flag['评论']:
                print('博文没有需要更新的')
                spider.crawler.engine.close_spider(spider, 'closespider')
            # 确保只加入新数据
            if self.info_flag['微博']:
                return
            check = "select * from " + name + '_微博 ' + "where sid=" + item['sid']
            self.cursor.execute(check)
            result = self.cursor.fetchall()
            if result:
                self.info_flag['微博'] = True
            insert = 'insert ignore into ' + name + '_微博 ' + \
                     '(sid, 创建时间, 文本, 发送设备, 阅读数, 转发数, 评论数, 点赞数, 话题, 发布于) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '
            self.cursor.execute(insert, [item['sid'], item['created_at'], item['text'], item['source'],
                                         item['reads_count'], item['reposts_count'], item['comments_count'],
                                         item['attitudes_count'], item['tag'], item['region_name']])
            self.connect.commit()
        # 传来的是Comment对象
        if isinstance(item, CommentItem):
            self.cursor.execute("use sina")
            self.cursor.execute("show tables")
            tables = self.cursor.fetchall()
            table_list = [t[0] for t in tables]
            name = settings.NAME.lower()
            if name + '_评论' not in table_list:
                print("名字(评论表单)：", name)
                sql = 'CREATE TABLE ' + name + '_评论 ' + \
                      '(所属博文 VARCHAR(255), cid VARCHAR(255) PRIMARY KEY, 评论时间 VARCHAR(255), 评论文本 VARCHAR(1024), ' \
                      '作者是否点赞 VARCHAR(255), 评论人id VARCHAR(255), 评论人昵称 VARCHAR(255), 评论点赞数 VARCHAR(255), ' \
                      '评论回复总数 VARCHAR(255), 评论回复内容 VARCHAR(1024));'  # 此处写的时候少了一个括号检查了好久
                self.cursor.execute(sql)
            else:
                pass
            # 如果两个都为True则终止程序
            if self.info_flag['微博'] and self.info_flag['评论']:
                print('评论没有需要更新的')
                spider.crawler.engine.close_spider(spider, 'closespider')
            # 确保只加入新数据
            if self.info_flag['评论']:
                return
            check = "select * from " + name + '_评论 ' + "where cid=" + item['cid']
            self.cursor.execute(check)
            result = self.cursor.fetchall()
            if result:
                self.info_flag['评论'] = True
            insert = 'insert ignore into ' + name + '_评论 ' + \
                     '(所属博文, cid, 评论时间, 评论文本, 作者是否点赞, 评论人id, 评论人昵称, 评论点赞数, 评论回复总数, 评论回复内容)' \
                     ' values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '
            self.cursor.execute(insert, [item['sid'], item['cid'], item['comment_time'], item['text'],
                                         item['liked'], item['comment_people_id'], item['comment_people_name'],
                                         item['comment_likes'], item['total_number'], str(item['comment_comment'])])
            self.connect.commit()
        return item
