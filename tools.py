# -*- coding: utf-8 -*-
import re
import requests
from lxml import etree
import random
import time
import json
# 存储商店链接
def Shopstxt(url):
    with open('shop_url.txt', 'a+') as f:
        f.write(url + '\n')

def Pjiatxt(url):
    with open('pjia_url.txt', 'a+') as f:
        f.write(url + '\n')
def ip():
    sde = "http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
    ips = requests.get(sde).text
    ips = ips.replace('\r\n', '')
    proxy_ip = {'http': ips}
    return proxy_ip


def getAtrr(prolist):
    attribute2 = []
    attribute = []
    if len(prolist) != 0:
        for each in prolist:
            each = " ".join(each.split())
            each = each.split('：')
            if len(each) == 1:
                each = each[0].split(':')
            # print(each)
            each = {"key": each[0], "value": each[1].strip()}
            attribute.append(each)
        for x in attribute:
            # print(x['key'])
            if ":" in x['key']:
                attr = x['key'] + x['value']
                attr = attr.split(':', 1)
                x['key'] = attr[0]
                x['value'] = attr[1]
            attribute2.append(x)
        return attribute2
    else:
        prolist = []
        return prolist

def getTime(value):
    alltime = re.compile(r'(\d{4}-\d{1,2}-\d{1,2})').findall(value)
    Production_date = {}
    if len(alltime) != 0:
        fromTime = alltime[0]
        endTime = alltime[1]
        Production_date = {
            "from_time":fromTime, "end_time":endTime
        }
        return Production_date
    else:
        Production_date = {
            "from_time":"", "end_time": ""
        }
        return Production_date

# 商店数据清洗工具
def getYear2(url):
    res = requests.get(url=url)
    content = etree.HTML(res.text)
    open_duration = content.xpath("//span[@class='tm-shop-age-content']/text()")
    if len(open_duration) > 0:
        open_duration = "".join(open_duration)
        num = re.compile(r"(\d+)").findall(open_duration)
        open_duration = "天猫" + str(num[0]) + "年店"
        return open_duration


def splitData1(value):
    value = value.split(',')
    return value

def splitData2(value):
    value = value.split(',')
    listData = []
    for x in value:
        if "%" in x:
            x = float(x.strip("%"))
            x = x/100
            x = round(x, 5)
        else:
            x = 0
        listData.append(x)

    if len(listData) != 3:
        listData.append(0)
    return listData


#获取商店的评分数据
def changeData(score, proportion):

    score = splitData1(score)
    if score[0]:
        content = float(score[0])
    if score[1]:
        attitude = float(score[1])
    if score[2]:
        keynote = float(score[2])

    contrast_list = []
    for i in range(0, 3):
        scro_1 = re.compile(r'<b></b><em>(.*?)%</em>').findall(str(proportion[i]))
        scro_2 = re.compile((r'<em>--------</em>')).findall(str(proportion[i]))
        if scro_1:
            scro_1 = round(float(scro_1[0])/ 100, 5)
            contrast_list.insert(i, scro_1)
        elif scro_2:
            contrast_list.insert(i, 0)
        # 这是在低于同行的数据
        else:
            scro_1 = re.compile(r"(d*[0-9]\.\d*[1-9])%").findall(str(proportion[i]))
            scro_1 = float("-" + str(scro_1[0]))
            scro_1 = round(scro_1 / 100, 5)
            contrast_list.insert(i, scro_1)

    datas = {
        "content":content,"attitude":attitude, "keynote":keynote,
        "content_contrast":contrast_list[0],"attitude_contrast":contrast_list[1],"keynote_contrast":contrast_list[2],

    }
    return datas





# 获取数字
def getNum(value):
    num = re.compile(r'(\d+)').findall(value)

    if "万" in value :
        num = ".".join(num)
        num = float(num)*10000

        return int(num)
    elif len(num) ==0:
        num = 0
        return num
    else:
        num = int(num[0])
        return num

# 通过json链接获取产品参数
def getCanshu(Pid):
    r = requests.get(
        "http://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey=12574478&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp1&data=%7B%22itemNumId%22%3A%22"+str(Pid)+"%22%7D")
    res = r.text
    att = re.compile(r'"baseProps":(.*?)]},{"itemId":').findall(res)
    soldNums = re.compile(r'\\\"sellCount\\\":\\\"(.*?)\\\"\,').findall(res)
    commiteNums =re.compile(r'\"commentCount\":\"(.*?)\"\,').findall(res)

    if len(soldNums)!= 0:
        soldNums = getNum(soldNums[0])
    else:
        soldNums = 0
    if len(commiteNums)!= 0:
        commiteNums = getNum(commiteNums[0])
    else:
        commiteNums = 0

    if len(att)!= 0:
        att = att[0].replace(']', '').replace('[', '')
        att = eval(att)
        attrs = []
        # at = json.loads(att)
        for x in att:
            # attrs.append(x)

            if x['key'] == "生产日期":
                production_date = x['value']
                production_date = production_date.replace('年','-').replace('月','-').replace('日','')
                production_date = getTime(production_date)
            else:
                production_date = {
                    "from_time": "", "end_time": ""
                }
            attrs.append(x)
        print("使用了详情页的json")
        data = {
            'attribute':attrs,'production_date':production_date,'soldNums':soldNums,
        'commiteNums':commiteNums,'flag':True
        }
        return data
    else:
        data = {'soldNums':soldNums,
        'commiteNums':commiteNums, 'flag':False}
        return data

#
# getCanshu(Pid="565265766576")