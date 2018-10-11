# -*- coding: utf-8 -*-
"""
*获取产品数据的请求链接
http://list.tmall.com//m/search_items.htm?page_size=60&page_no=1&q=%BA%EC%BE%C6&style=g
item_id 为产品Id
shop_id可为拼接为shop_id
使用
"""
import time
import requests
import lxml.html
import csv
import pymongo
from bs4 import BeautifulSoup
import re
import collections
import hashlib
import urllib.request
import json
import random
import datetime
from lxml import etree
from tools import getAtrr, getTime, ip,Shopstxt,Pjiatxt,getCanshu, getNum
from User_agent import agents

client = pymongo.MongoClient('192.168.0.24', 27701)
db = client.beehive

# client = pymongo.MongoClient('127.0.0.1', 27017)
# db = client.test
agent = random.choice(agents)

headers = {
    'Proxy-Connection': 'keep-alive',

    'cookie': 't=af327e3856ea4d65d82c6e68f3348a2d; cna=tDAmFLw/fFACAXb5bDfpTqKh; thw=cn; v=0; cookie2=1664fb83a95cebb14e25281ca9a01022; _tb_token_=e853915ee6ee; unb=177514767; sg=e79; _l_g_=Ug%3D%3D; skt=8f4891719209b454; cookie1=BYEH22ZgOEjDZR7QEfw066B6gcYb5p84e20aQjCzDhU%3D; csg=0d282580; uc3=vt3=F8dByRquF3C26KWCxDw%3D&id2=UoYZbxpKI7a0&nk2=B0PqOlwJHHG604uU6Wc%2BGg%3D%3D&lg2=UtASsssmOIJ0bQ%3D%3D; existShop=MTUzOTE2NTU3Nw%3D%3D; tracknick=daviddavidleelee; lgc=daviddavidleelee; _cc_=WqG3DMC9EA%3D%3D; dnk=daviddavidleelee; _nk_=daviddavidleelee; cookie17=UoYZbxpKI7a0; tg=0; mt=ci=110_1; enc=nh3yectXXCIWA0IQbF8de5bwGI0K%2B%2BLGtLiPmzVTvMStWnhfbWsYO6YOOvO9HTl1qNPpmpygv%2F3wAMDbnZRZ2A%3D%3D; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; JSESSIONID=AD82F6571F45F22ED954637D2544CFCD; uc1="cookie15=URm48syIIVrSKA%3D%3D"; hng=CN%7Czh-CN%7CCNY%7C156; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; swfstore=139632; isg=BE9Pg1EfSPvgWUyAodhs6Gua3uP1Z_PKgT-6z2Fcyb7FMG4yaUXv550oNmCOSHsO',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',

}

# 拿到每一页的数据
# def get_pageList():
#
#     for d in range(4, 101):
#         # time.sleep(random.choice(range(1, 3)))
#         print(str(d) + "page")
#         # proxy = ip()
#         url = 'http://list.tmall.com//m/search_items.htm?page_size=60&page_no='+str(d)
#         response = requests.get(url,headers = headers)
#         # response = requests.get(url, headers=headers, proxies=proxy)
#         res = json.loads(response.text)
#         get_content(res)
#         print("---------------over--------------------------")
def Porducts():

    with open("prolist.txt", 'r', encoding="utf-8") as f:
        eachs = f.readlines()
        eachs = [x.strip('\n') for x in eachs]
        i = 0
        for x in eachs:
            if x != "":
                each = json.loads(x)
                i += 1
                print(str(i)+"页")
                get_content(each)

                print("---------------over--------------------------")

#将页面数据进行
def get_content(res):

    for pro_data in res['item']:
        item_id = str(pro_data['item_id'])
        _id = hashlib.md5(item_id.encode()).hexdigest()
        shop_id = str(pro_data['shop_id'])
        # 商店链接
        shop_url = "https://hdc1.alicdn.com/asyn.htm?userId="+shop_id

        user_id = hashlib.md5(shop_id.encode()).hexdigest()
        sku_id = pro_data['sku_id']
        detail_url = "https://detail.tmall.com/item.htm?id="+str(item_id)+"&skuId="+str(sku_id)+"&areaId=440300&user_id="+str(shop_id)+"&cat_id=2&is_b=1"
        titles = pro_data['title']
        location = pro_data['location']
        prices = float(pro_data['price'])
        # trading = getNum(pro_data['sold'])
        # count = getNum(pro_data['comment_num'])

        local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        spider_time = "20181010"
        listlcon = pro_data['listIcon']
        listlcon = str(listlcon)
        # time.sleep(random.choice(range(1,3)))
        get_proKey(detail_url)
        canshu  = get_proKey(detail_url)
        trading = canshu['trading']
        count = canshu['count']
        # 评价链接
        pjia = 'https://rate.tmall.com/list_detail_rate.htm?itemId=' + str(canshu['idd']) + '&spuId=' + str(canshu['at_prid']) + '&sellerId=' + shop_id + '&order=3&currentPage='

        attribute = canshu['attribute']

        if "进口" in listlcon or "进口" in titles:
            entrance = "原瓶进口"
        else:
            entrance = "国产"

        if len(canshu['open_duration']) != 0:
            open_duration = canshu['open_duration'][0]
        else:
            open_duration = ""

        production_date = canshu['production_date']

        datas = {
            '_id': _id, 'url': detail_url, 'prices': prices, 'titles': titles, 'trading': trading,
            'count': count, 'entrance': entrance, 'attribute': attribute, 'open_duration': open_duration,
            'production_date': production_date,
            'user_id': user_id, 'local_time': local_time, 'spider_time': spider_time
        }
        try:
            db_list = db.products_copys
            db_list.update_one({'_id': datas['_id']}, {'$set': dict(datas)}, upsert=True)
            print(_id + "***sucess-data***"+item_id)
            Pjiatxt(pjia)
            Shopstxt(shop_url)
        except Exception as e:
            print(_id+"faild-data"+item_id)

def get_proKey(url):
    try:
        request = urllib.request.Request(url=url, headers=headers, method='GET')
        response = urllib.request.urlopen(request)
        htmlPage = response.read().decode('gbk')

        res = etree.HTML(htmlPage)

        req = response.headers
        at_prid = req['at_prid']
        idd = req['at_itemid']
        open_duration = res.xpath("//span[@class='tm-shop-age-content']/text()")

        Pid =re.compile(r'\?id=(.*?)&').findall(str(url))
        canchuFlag = getCanshu(Pid[0])
        if canchuFlag['flag'] == False:
            attr = res.xpath("//*[@id='J_AttrUL']/li//text()")
            pro_date = res.xpath("//*[@class='tb-validity']//text()")
            pro_date = "".join(pro_date)

            attribute = getAtrr(attr)
            production_date = getTime(pro_date)
        else:
            attribute = canchuFlag['attribute']
            production_date = canchuFlag['production_date']
        trading = canchuFlag['soldNums']
        count = canchuFlag['commiteNums']
        canshu = {'trading':trading,'count':count,'attribute':attribute,'open_duration':open_duration, 'production_date':production_date,'at_prid':at_prid,'idd':idd}
        return  canshu
    except Exception as e:
        print("detail-faild("+url+")", e)

# get_proKey(url = 'https://detail.tmall.com/item.htm?id=43724784272&skuId=4611686062152172176&areaId=440300&user_id=2380530097&cat_id=2&is_b=1')

if __name__ == "__main__":
    Porducts()
    # get_proKey(url="https://detail.tmall.com/item.htm?id=566930662860&areaId=440300&user_id=3430748706&cat_id=2&is_b=1")
    # get_proKey(url="https://detail.tmall.com/item.htm?id=540226087282&skuId=3202944271278&areaId=440300&user_id=2630035235&cat_id=2&is_b=1")