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
from cookies import cookies

client = pymongo.MongoClient('192.168.0.24', 27701)
db = client.beehive

# client = pymongo.MongoClient('127.0.0.1', 27017)
# db = client.test
cookie = random.choice(cookies)
headers = {

    'cookie': 'lid=%E5%88%AB%E6%8A%A2%E6%88%91%E7%9A%84%E9%AA%A8%E5%A4%B4; uss=""; cna=V2EmFFWEkVkCAXb5bDc9xJPn; _med=dw:1920&dh:1080&pw:1920&ph:1080&ist:0; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; x=__ll%3D-1%26_ato%3D0; _uab_collina=153904979742202522545786; sm4=430103; t=dd11eb947bef185a4fed3208fa1996e0; tracknick=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; lgc=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; _tb_token_=107e57843798; cookie2=1cef4ea64137f6f3c309923c37087eea; uc3=vt3=F8dByRquFlVnAofL%2B1M%3D&id2=UoYY4HzALqv1Gg%3D%3D&nk2=0rWamFEWBzoitBU2&lg2=VT5L2FSpMGV7TQ%3D%3D; _l_g_=Ug%3D%3D; ck1=""; unb=1763525159; cookie1=Bqqu%2BFQ2xmXE5KKUSsig6bRgPnYT%2FWXq2pkn3r8LOeU%3D; login=true; cookie17=UoYY4HzALqv1Gg%3D%3D; _nk_=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; csg=fcb49508; skt=d085c45e05f750e7; _umdata=E2AE90FA4E0E42DEF9D18637572CD3FBA9B62757D7DF25F613E8940E54E5AECE70B38FA3E599C1FDCD43AD3E795C914C0DCA837C7ACD2F4854149E4207993A13; _m_h5_tk=faa3c76149f7c5d90609e890febd67ed_1539162631569; _m_h5_tk_enc=6647087ba20ecc07cd5ce1ba1f9d1f56; tt=food.tmall.com; swfstore=169921; dnk=%5Cu522B%5Cu62A2%5Cu6211%5Cu7684%5Cu9AA8%5Cu5934; hng=CN%7Czh-CN%7CCNY%7C156; uc1=cookie15=VFC%2FuZ9ayeYq2g%3D%3D; sg=%E5%A4%B49e; res=scroll%3A1583*5575-client%3A1583*307-offset%3A1583*5575-screen%3A1600*900; pnm_cku822=098%23E1hvbQvUvbpvUpCkvvvvvjiPPschljEvPsFwAjljPmPvgjlEPLdwtjiEnL5ZzjrbPpGCvvpvvvvvvphvC9vhphvvvvyCvhAvgetKjXZpeEIaWDNBlLyzhbUfbzc6%2Bu6Xd5QXfaAKHd8rakS63b8rVut%2BCNoxdBKK5znbAWva5EAXJHLXSfpAhC3qVUcn%2B3mOVzIUkphvC9hvpyPOt8yCvv9vvhh5ao9WZqyCvm9vvhCvvvm2pvvvB9OvvUmXvvCVC9vv9ZUvvhOVvvmCb9vvB9OvvUhKRphvCvvvphm5vpvhvvCCBv%3D%3D; whl=-1%260%260%260; x5sec=7b22746d616c6c7365617263683b32223a223862346261383937393564303637323934336636343230303037653463666361434f2f7039743046454f323339624b44757458684f426f4d4d5463324d7a55794e5445314f547378227d; isg=BD4-RM_p6VRwXD1Sa_rBrY9wj1QsbFKcemkZB-hHlQF8i99lUAwjCZtqBxfis_oR',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',

}

# 拿到每一页的数据
def get_pageList():

    for d in range(2, 101):
        # time.sleep(random.choice(range(1, 3)))
        print(str(d) + "page")
        proxy = ip()
        url = 'http://list.tmall.com//m/search_items.htm?page_size=60&page_no='+str(d)+'&q=%BA%EC%BE%C6&style=g'
        response = requests.get(url,headers = headers, proxies={'http':'27.209.167.77:4243'})
        # response = requests.get(url, headers=headers, proxies=proxy)
        res = json.loads(response.text)
        get_content(res)
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
        time.sleep(random.choice(range(1,3)))
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

        Pid =re.compile(r'id=(.*?)&skuId').findall(str(url))
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
    get_pageList()
    # get_proKey(url="https://detail.tmall.com/item.htm?id=524510363572&skuId=3202944271278&areaId=440300&user_id=2630035235&cat_id=2&is_b=1")
    # get_proKey(url="https://detail.tmall.com/item.htm?id=540226087282&skuId=3202944271278&areaId=440300&user_id=2630035235&cat_id=2&is_b=1")