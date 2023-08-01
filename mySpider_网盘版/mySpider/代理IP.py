# coding=utf-8
import re
import requests


def get_ip(typ='free'):
    # 请求地址 简单提取 具体需要根据实际情况获取 记得添加白名单 http://www.siyetian.com/member/whitelist.html
    if typ == 'free':
        # tiquApiUrl = 'http://proxy.siyetian.com/apis_get.html?token=gHbi1iTqlkMNR1aw8EVZdXTn1STqFUeNpXQw0kaRlXTEVVMPR0az0EVjl3TEFle.gMwcDM1gjM4YTM&limit=1&type=0&time=&split=1&split_text=&area=0&repeat=0&isp=0'
        tiquApiUrl = 'http://proxy.siyetian.com/apis_get.html?token=gHbi1iTqlkMNR1aw8EVZdXTn1STqFUeNpXQw0kaRlXTEVVMPR0az0EVjl3TEFle.QN2QDN1UDM5YTM&limit=1&type=0&time=&split=1&split_text=&repeat=0&isp=0'
    elif typ == 'paid':
        tiquApiUrl = 'http://proxy.siyetian.com/apis_get.html?token=AesJWLORVUx0ERJdXTq10dORUSw4kaVFTTB1STqFUeNpXQw0kaRlXTEVVMPR0az0EVjl3TEFle.QNykDOwMjM4YTM&limit=1&type=0&time=&split=1&split_text=&area=0&repeat=0&isp=0'

    else:
        raise SystemExit('输入套餐类型不合法')
    apiRes = requests.get(tiquApiUrl, timeout=5)
    # 代理服务器
    ipport = apiRes.text
    # 返回错误代码
    if "code" in ipport:
        print(typ + " IP申请失败, code: " + ipport)
        code = re.findall(':(.*?),', ipport)[0]
        return "code:" + code
    return ipport
