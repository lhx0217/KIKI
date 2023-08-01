import pymysql

def del_all_tables(cursor):
    cursor.execute("show tables")
    tables = cursor.fetchall()
    table_list = [t[0] for t in tables]
    for name in table_list:
        cmd = 'drop table if exists ' + name
        cursor.execute(cmd)
    cursor.execute("show tables")
    tables = cursor.fetchall()  # 查询结果
    print(tables)

if __name__ == "__main__":
    # 创建数据库链接

    db = pymysql.connect(
        host="localhost",  # 主机ip
        user="root",  # 数据库用户
        password="qwe127227472",  # 用户对应的密码
        database="sina",  # 对应的数据库
        port=3306,  # 数据库端口，默认3306
        charset='utf8'  # 数据库编码
    )
    # 创建游标:游标用于传递python给mysql的命令和mysql返回的内容
    cursor = db.cursor()
    # del_all_tables(cursor)
    # 执行部分
    cursor.execute("use sina")
    # del_all_tables(cursor)
    cursor.execute("show tables")

    tables = cursor.fetchall()  # 查询结果
    print(tables)
    if tables:
        print('something')
    del_all_tables(cursor)
    # cursor.execute("CREATE TABLE test (uid VARCHAR(255), 昵称 VARCHAR(255), 真实姓名 VARCHAR(255), "
    #                "所在地 VARCHAR(255), 性别 VARCHAR(255), 生日 VARCHAR(255), QQ VARCHAR(255), 简介 VARCHAR(255), "
    #                "粉丝数 VARCHAR(255), 关注数 VARCHAR(255),  微博数 VARCHAR(255), 微博认证用户 VARCHAR("
    #                "255), 注册时间 VARCHAR(255), 微博会员等级 VARCHAR(255), 职业信息 VARCHAR(255), 教育信息 VARCHAR(255))")

    # 关闭部分
    db.commit()  # 链接提交，用于对数据库的增删改
    cursor.close()  # 关闭游标
    db.close()  # 关闭链接


