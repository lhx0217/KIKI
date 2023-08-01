from flask import Flask
from flask import render_template
from flask import request
from pymysql import *
import json
import multiprocessing
from mySpider.run import *
import mySpider.main as driver

app = Flask(__name__)
MYSQL_HOST = "localhost"
MYSQL_DBNAME = "sina"
MYSQL_USER = "root"
MYSQL_PASSWD = ""
NAME = ""
test_name = "summerwwxxyy"
# 修改提示信息功能暂未实现
def get_wb_id(name):
    APP_KEY = ''
    APP_SECRET = ''
    CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
    USER_NAME = '用户9876583554'
    PASSWORD = ''
    try:
        wb_info = driver.WeiBoInfo(APP_KEY, APP_SECRET, CALLBACK_URL, USER_NAME, PASSWORD)
        return wb_info.search_user(name=name)
    except Exception as err:
        print(err)
        return ' '

@app.route('/', methods=['GET', 'POST'])
def search():
    # 替换html中的information字段
    context = {"infomation": "输入不能为空"}
    return render_template('index.html', **context)

@app.route('/search.html')
def user_info():
    NAME = request.args.get('searchname')
    connection = connect(host=MYSQL_HOST, db=MYSQL_DBNAME, user=MYSQL_USER, passwd=MYSQL_PASSWD, use_unicode=True)
    cursor = connection.cursor()
    cursor.execute("use sina")

    # 如果搜索的用户名不在数据库目录中则重新爬取
    ID = get_wb_id(NAME)
    # 如果返回没有找到该用户,则让浏览器显示错误输入
    if ID == "no specific user":
        context = {"infomation": "输入用户名错误"}
        return render_template('index.html', **context)
    elif ID == " ":
        context = {"infomation": "修改main的cookie"}
        return render_template('index.html', **context)
    data = {'NAME': NAME, "ID": ID}
    # 设置settings中的NAME和ID
    with open('name.json', 'w+') as fil:
        json.dump(data, fil)
    parent_conn, child_conn = multiprocessing.Pipe()
    # 多进程运行爬虫（否则报错loop error）, 是否输出log信息
    child_process = multiprocessing.Process(target=run_crawler, args=(child_conn, False))
    # 启动子进程
    child_process.start()
    # 等待子进程结束
    child_process.join()
    child_return = parent_conn.recv()
    # 只有报错了才会返回
    if type(child_return) == SystemExit:
        print(child_return)
        context = {"infomation": "IP申请失败"}
        return render_template('index.html', **context)
    else:
        print(child_return)

    # 存json文件
    cursor.execute("show tables")
    tables = cursor.fetchall()
    for table in tables:
        total = []
        cursor.execute("select * from " + table[0])
        data = cursor.fetchall()
        # 显示每列的详细信息
        des = cursor.description
        header = [item[0] for item in des]
        for num in range(len(data)):
            temp_dic = {}
            info = data[num]
            for index in range(len(header)):
                if "时间" in header[index]:
                    date = info[index].replace("+0800", "")
                else:
                    date = info[index]
                if header[index] == "标签":
                    temp_dic["________________" + header[index] + "________________"] = date
                else:
                    temp_dic[header[index]] = date
            total.append(temp_dic)
        with open("./static/json/" + table[0] + ".json", 'w+') as js:
            json.dump(total, js)
    context = {
        "NAME": NAME,
    }
    return render_template('search.html', **context)

@app.route('/chart.html')
def muban():
    return render_template('chart.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=False, port=8080)
