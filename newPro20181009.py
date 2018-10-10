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
from tools import getAtrr, getTime, ip,Shopstxt,Pjiatxt

# client = pymongo.MongoClient('192.168.0.24', 27701)
# db = client.beehive

client = pymongo.MongoClient('127.0.0.1', 27017)
db = client.test
headers = {

    'cookie': 't=dd11eb947bef185a4fed3208fa1996e0; lid=%E5%88%AB%E6%8A%A2%E6%88%91%E7%9A%84%E9%AA%A8%E5%A4%B4; _tb_token_=e353beeb0ea38; cookie2=1769010fbd11ef956a7c578f3f9e7bc9; hng=""; uc1=cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&cookie21=UIHiLt3xSifiVqTH8o%2F0Qw%3D%3D&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&existShop=false&pas=0&cookie14=UoTfItCjhY%2BTbA%3D%3D&tag=8&lng=zh_CN; uc3=vt3=F8dByRqvPiu9qwhtIus%3D&id2=UoYY4HzALqv1Gg%3D%3D&nk2=0rWamFEWBzoitBU2&lg2=VFC%2FuZ9ayeYq2g%3D%3D; tracknick=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; _l_g_=Ug%3D%3D; unb=1763525159; lgc=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; cookie1=Bqqu%2BFQ2xmXE5KKUSsig6bRgPnYT%2FWXq2pkn3r8LOeU%3D; login=true; cookie17=UoYY4HzALqv1Gg%3D%3D; _nk_=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; uss=""; csg=d8ade8ed; skt=93325bba06580d02; cna=V2EmFFWEkVkCAXb5bDc9xJPn; _m_h5_tk=e77db747c89d2565032493426b1747d0_1539058142429; _m_h5_tk_enc=d6e60b3ef4145346065573db337dd94d; c=""; enc=KWxSAjXSv%2B%2FBPZpCbNR8DlRUEVFW9RvmZ6e94YkhbvM9DdHmG%2FfiPbHM5%2BtLCPFfgtpKLX%2Bpt1EV%2FVLzNc%2BqkA%3D%3D; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; whl=-1%260%260%260; isg=BHFxJi0sjrzvciKLsHvGNOShgP2nTbW1YfgmPlOGZThXepHMm6tAoA6UmE65sn0I',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',

}

# 拿到每一页的数据
def get_pageList():

    for d in range(6, 101):
        # time.sleep(random.choice(range(1, 3)))
        proxy = ip()
        url = 'http://list.tmall.com//m/search_items.htm?page_size=60&page_no='+str(d)+'&q=%BA%EC%BE%C6&style=g'
        response = requests.get(url,headers = headers, proxies=proxy)
        res = json.loads(response.text)
        get_content(res)
        print(str(d)+"page")

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
        trading = int(pro_data['sold'])
        count = int(pro_data['comment_num'])
        local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        spider_time = "20181010"
        listlcon = pro_data['listIcon']
        listlcon = str(listlcon)
        time.sleep(random.choice(range(1,3)))
        get_proKey(detail_url)
        canshu  = get_proKey(detail_url)

        # 评价链接
        pjia = 'https://rate.tmall.com/list_detail_rate.htm?itemId=' + str(canshu['idd']) + '&spuId=' + str(canshu['at_prid']) + '&sellerId=' + shop_id + '&order=3&currentPage='

        attribute = canshu['attribute']
        # if len(attribute) != 0:
        #     att = "".join(attribute)
        # else:
        #     att = ""
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
            db_list = db.liheng
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

        attr = res.xpath("//*[@class='J_subAttrList']/li//text()")
        pro_date = res.xpath("//*[@class='tb-validity']//text()")
        open_duration = res.xpath("//span[@class='tm-shop-age-content']/text()")
        pro_date = "".join(pro_date)

        attribute = getAtrr(attr)

        foodProDate = re.compile(r'"foodProDate":(.*?),').findall(htmlPage)
        if len(foodProDate) !=0:
            production_date = getTime(foodProDate)
        else:
            production_date = getTime(pro_date)
        canshu = {'attribute':attribute,'open_duration':open_duration, 'production_date':production_date,'at_prid':at_prid,'idd':idd}
        return canshu
    except Exception as e:
        print("detail-faild("+url+")", e)

# get_proKey(url = 'https://detail.tmall.com/item.htm?id=43724784272&skuId=4611686062152172176&areaId=440300&user_id=2380530097&cat_id=2&is_b=1')

if __name__ == "__main__":
    # get_pageList()
    get_proKey(url="https://detail.tmall.hk/hk/item.htm?id=540226087282&skuId=3202944271278&areaId=440300&user_id=2630035235&cat_id=2&is_b=1")