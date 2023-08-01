# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class UserItem(scrapy.Item):
    """用户信息字段"""
    # 告诉pipeline得到的是粉丝还是关注者还是自己, 0->自己, 1->粉丝, 2->关注的人
    group = scrapy.Field()
    # 用户ID
    uid = scrapy.Field()
    # 用户昵称
    screen_name = scrapy.Field()
    # 粉丝数
    followers_count = scrapy.Field()
    # 关注数
    follow_count = scrapy.Field()
    # 简介
    description = scrapy.Field()
    # 性别
    gender = scrapy.Field()
    # 位置
    location = scrapy.Field()
    # 微博数量
    statuses_count = scrapy.Field()
    # 否是微博认证用户，即加V用户
    verified = scrapy.Field()
    # 用户的微博会员等级，0：普通用户、1-6：微博会员等级
    mbrank = scrapy.Field()
    # 生日
    birthday = scrapy.Field()
    # 注册时间
    regist_time = scrapy.Field()
    # QQ
    qq = scrapy.Field()
    # 真实姓名
    real_name = scrapy.Field()
    # 职业信息
    profession = scrapy.Field()
    # 教育信息
    education = scrapy.Field()
    # 标签
    lable = scrapy.Field()
    # 信誉
    credit = scrapy.Field()
    # ip属地
    ip_location = scrapy.Field()


class CommentItem(scrapy.Item):
    """评论字段"""
    # 所属博文
    sid = scrapy.Field()
    # 评论标识
    cid = scrapy.Field()
    # 评论时间
    comment_time = scrapy.Field()
    # 评论文本
    text = scrapy.Field()
    # 作者是否点赞
    liked = scrapy.Field()
    # 评论人id
    comment_people_id = scrapy.Field()
    # 评论人昵称
    comment_people_name = scrapy.Field()
    # 评论点赞数
    comment_likes = scrapy.Field()
    # 评论回复总数
    total_number = scrapy.Field()
    # 评论回复内容
    comment_comment = scrapy.Field()

class StatusesItem(scrapy.Item):
    """微博字段"""
    # 标识号
    sid = scrapy.Field()
    # 创建时间
    created_at = scrapy.Field()
    # 文本
    text = scrapy.Field()
    # 发送设备
    source = scrapy.Field()
    # 阅读数
    reads_count = scrapy.Field()
    # 转发数
    reposts_count = scrapy.Field()
    # 评论数
    comments_count = scrapy.Field()
    # 点赞数
    attitudes_count = scrapy.Field()
    # 话题
    tag = scrapy.Field()
    # 发布于
    region_name = scrapy.Field()