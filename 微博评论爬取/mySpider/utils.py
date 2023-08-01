import re


def print_user_info(user):
    """
    有用的字段:
        text: 【#5件事缓解睡眠焦虑#】近日，话题#千万不要在夜里醒来看时间#引发热议，日本睡眠管理医生菅原洋平表示，越是在夜(折叠前的字)
        textLength: 1358
        favorited: 是否已收藏, False
        truncated: 是否被截断, False
        user字段 (该条微博的用户信息/重要)
        id: 用户的唯一标识符, 2028810631
        screen_name: 用户的昵称, 新浪新闻
        province: 用户所在省份的代码, 11
        city: 用户所在城市的代码, 1000
        location: 用户所在地, 北京
        description: 用户个人描述,  '上新浪新闻客户端，每天了解世界多一点。下载客户端：https://sina.cn/j/d.php?k=87'
        weihao: 用户的微号, ''
        gender: 用户的性别，m：男、f：女、n：未知, m
        followers_count: 粉丝数, 9405.4万
        friends_count: 关注数, 2013
        statuses_count: 微博数 ,118206
        favourites_count: 收藏数, 111
        created_at: 用户创建（注册）时间, Wed Mar 16 10:18:43 +0800 2011
        allow_all_act_msg: 是否允许所有人给我发私信
        verified: 是否是微博认证用户，即加V用户
        remark: 用户备注信息，只有在查询用户关系时才返回此字段
        allow_all_comment: 是否允许所有人对我的微博进行评论
        star: 用户是否是微博达人
        mbrank: 用户的微博会员等级，0：普通用户、1-6：微博会员等级
        urank: 用户的微博等级
        retweeted_status: 转发的博文，内容为status，如果不是转发，则没有此字段
    """
    print("=" * 20, user["id"], user["screen_name"], "=" * 20)


def operate_cookies(cookie):
    dic = {}
    c_l = cookie.split("; ")
    for item in c_l:
        k_n = item.split('=')
        dic[k_n[0]] = k_n[1]
    # new_dic = {'XSRF-TOKEN': dic['XSRF-TOKEN'], 'SUB': dic['SUB'], 'SUBP': dic['SUBP'], 'WBPSESS': dic['WBPSESS']}
    return dic


def standardize_sentence(sentence):
    p = re.compile(
        u'['u'\U0001F300-\U0001F64F' u'\U0001F680-\U0001F6FF' u'\u2600-\u2B55 \U00010000-\U0010ffff]+')
    sentence = re.sub(p, '', sentence).replace('​', '')
    return sentence


def gen_user_info(item, dic):
    item['uid'] = dic["idstr"]
    item['screen_name'] = dic["screen_name"]
    item['followers_count'] = dic["followers_count"]
    item['follow_count'] = str(dic["friends_count"])
    item['gender'] = dic['gender']
    # 消除无法识别的字符
    item['description'] = standardize_sentence(dic['description'])
    item['location'] = dic['location']
    item['statuses_count'] = str(dic['statuses_count'])
    item['verified'] = str(dic['verified'])
    item['mbrank'] = str(dic['mbrank'])
    return item


def gen_user_detail(item, dic):
    key_list = dic.keys()
    if 'birthday' in key_list:
        item['birthday'] = dic['birthday']
    else:
        item['birthday'] = ''
    item['regist_time'] = dic['created_at']
    if 'education' in key_list:
        item['education'] = dic['education']['school']
    else:
        item['education'] = ''
    if 'career' in key_list:
        item['profession'] = dic['career']['company']
    else:
        item['profession'] = ''
    if 'ip_location' in key_list:
        item['ip_location'] = dic['ip_location']
    else:
        item['ip_location'] = ''
    # 把标签合成为一个进行保存
    if 'label_desc' in key_list:
        item['lable'] = " ".join([n['name'] for n in dic['label_desc']])
    else:
        item['lable'] = ''
    if 'sunshine_credit' in key_list:
        item['credit'] = dic['sunshine_credit']['level']
    else:
        item['credit'] = ''
    item['real_name'] = ''
    item['qq'] = ''
    return item


def gen_statuses_info(item, dic):
    key_list = dic.keys()
    item['created_at'] = dic['created_at']
    item['sid'] = dic['idstr']
    item['text'] = standardize_sentence(dic['text_raw'])
    # source如果使用手机发送的如OPPO会显示一大串
    source = dic['source']
    if len(source) > 20:
        op = re.findall(r'>(.*?)</a>', source)
        item['source'] = '||'.join(op)
    else:
        item['source'] = source

    item['reads_count'] = dic['reads_count']
    item['reposts_count'] = dic['reposts_count']
    item['comments_count'] = dic['comments_count']
    item['attitudes_count'] = dic['attitudes_count']

    if 'topic_struct' in key_list:
        tag = []
        for topic in dic['topic_struct']:
            tag.append(standardize_sentence(topic['topic_title']))
        item['tag'] = '||'.join(tag)
    else:
        item['tag'] = ''

    if 'region_name' in key_list:
        item['region_name'] = dic['region_name']
    else:
        item['region_name'] = ''
    return item


def gen_comment_info(item, dic, sid):
    item['sid'] = sid
    item['cid'] = dic['idstr']
    item['comment_time'] = dic['created_at']
    item['text'] = standardize_sentence(dic['text_raw'])
    item['liked'] = str(dic['isLikedByMblogAuthor'])
    item['comment_people_id'] = dic['user']['idstr']
    item['comment_people_name'] = dic['user']['screen_name']
    item['comment_likes'] = dic['like_counts']
    item['total_number'] = dic['total_number']
    if 'comments' in dic.keys():
        comment_list = dic['comments']
        comment_comment = []
        for comment in comment_list:
            comment_comment.append(standardize_sentence(comment['text_raw']))
        item['comment_comment'] = comment_comment
    else:
        item['comment_comment'] = ''
    return item


if __name__ == "__main__":
    # cookies = 'XSRF-TOKEN=dHcugN5oTbSsRgZBbc5s1Qil; _s_tentry=weibo.com; Apache=3317105541113.3545.1679984592798; SINAGLOBAL=3317105541113.3545.1679984592798; ULV=1679984592847:1:1:1:3317105541113.3545.1679984592798:; login_sid_t=5cc78f848930a4a80da204d51d74d168; cross_origin_proto=SSL; wb_view_log=1536*8641.25; SSOLoginState=1680053951; SUB=_2A25JJ-bvDeRhGeFG6VsU9ifNzD2IHXVqVV8nrDV8PUNbmtAGLUyskW9NecuFqBdf50lga_3Z9y0i6UoMYwEaMTYl; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWYBr.gsLP6dXfcYWznKdh.5JpX5KzhUgL.FoMReo.fSo.pS022dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM41hMcSKn0SK-X; ALF=1711589950; PC_TOKEN=648b7422b4; WBPSESS=cr4hkwwxfJb_HtFDhT8YoC0YE2NMcVda9jxGBXyZ-_xMYIvQcUU812qHfyJyCWTIcwSsR9zru4ScrsdgO9jilJqdFjPi5k2GMzDK_Eau-wUA43ovlNRbT0NXijosIdYnFyyO0RDPNzlNhmxDoazPyA=='
    # cookies = 'PC_TOKEN=8fea69af01; login_sid_t=9da87c418c11b7b9059c60555fb77552; cross_origin_proto=SSL; WBStorage=4d96c54e|undefined; XSRF-TOKEN=1AoeH41faR09_jP0MAenmvwb; wb_view_log=1500*10002; _s_tentry=passport.weibo.com; Apache=3374093186368.1943.1682302781087; SINAGLOBAL=3374093186368.1943.1682302781087; ULV=1682302781090:1:1:1:3374093186368.1943.1682302781087:; SUB=_2A25JQZcpDeThGeFK7FoT9SrEyj6IHXVqNo_hrDV8PUNbmtANLWfMkW9NQuy80jxwZrGTh-EMbnzDgBEypQ-scGlg; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWOHT.GBaf.T14Fkq4vZsZy5JpX5KzhUgL.FoMXS0nESKBReKz2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNShMReo-X1h2E; ALF=1713838841; SSOLoginState=1682302841; WBPSESS=N0o07z925RNG4dSBXH43bWOAm10MH3ImSBYOci3TT7COd19fhRoP83GmWFEFjtLxklJqd3RMGEhOcLPA1uRQE6Y9tWR1BWEJKFcakaATBgkT9UWOxftZB1JU1w4MzjHP5PyQFA3W79u8WS1sxnmmnw=='
    cookies = r'SINAGLOBAL=854091521546.8892.1681147181385; UOR=,,www.baidu.com; XSRF-TOKEN=fZVEIjyh2L8Z2r6sNF6EjlQC; SSOLoginState=1687164216; _s_tentry=weibo.com; Apache=5434106121261.56.1687182900766; ULV=1687182900844:9:1:1:5434106121261.56.1687182900766:1682870959293; PC_TOKEN=5d8706880d; SCF=AmvalvHGBo3cbUEZ0zYRzQDBfoS9f7yiuhkagWnVzHFqvtEjBYah6jNZexnX9w9C0Y2qumUdZVKXmaoezV5NozU.; SUB=_2A25JlBYJDeRhGeFG6VsU9ifNzD2IHXVq4ADBrDV8PUNbmtANLWbckW9NecuFqH-xdXpmANLL8D_JeAfjp_1GbxDj; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWYBr.gsLP6dXfcYWznKdh.5JpX5KzhUgL.FoMReo.fSo.pS022dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM41hMcSKn0SK-X; ALF=1718720984; WBPSESS=Dt2hbAUaXfkVprjyrAZT_HcDnrIsBeAB8QRpAS-qJhF1LS81_yXGRsZWOuOKcexTUWlEoH2JRuGpQq5Xr_LIK8Saf_6z7uYslQF64-qlzUBkePSA70wm4WpxoH48-AlxaqmRKA1uLETsQTQEjm82P3-GaAvHJDvqqNc2DHoGaDn8ldHgPUEs8UKfswGU7Rp5129Qukf6pf-u4mRBwVXTyA=='
    operate_cookies(cookies)
