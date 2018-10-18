# -*- coding: utf-8 -*-
"""
更新现有产品数据
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

# client = pymongo.MongoClient('127.0.0.1', 27017)
# db = client.test

client = pymongo.MongoClient('192.168.0.24', 27701)
db = client.beehive
table = db['products']
print(type(table))
document = table.find()

headers = {
    'Proxy-Connection': 'keep-alive',

    'cookie': 't=af327e3856ea4d65d82c6e68f3348a2d; cna=tDAmFLw/fFACAXb5bDfpTqKh; thw=cn; v=0; cookie2=1664fb83a95cebb14e25281ca9a01022; _tb_token_=e853915ee6ee; unb=177514767; sg=e79; _l_g_=Ug%3D%3D; skt=8f4891719209b454; cookie1=BYEH22ZgOEjDZR7QEfw066B6gcYb5p84e20aQjCzDhU%3D; csg=0d282580; uc3=vt3=F8dByRquF3C26KWCxDw%3D&id2=UoYZbxpKI7a0&nk2=B0PqOlwJHHG604uU6Wc%2BGg%3D%3D&lg2=UtASsssmOIJ0bQ%3D%3D; existShop=MTUzOTE2NTU3Nw%3D%3D; tracknick=daviddavidleelee; lgc=daviddavidleelee; _cc_=WqG3DMC9EA%3D%3D; dnk=daviddavidleelee; _nk_=daviddavidleelee; cookie17=UoYZbxpKI7a0; tg=0; mt=ci=110_1; enc=nh3yectXXCIWA0IQbF8de5bwGI0K%2B%2BLGtLiPmzVTvMStWnhfbWsYO6YOOvO9HTl1qNPpmpygv%2F3wAMDbnZRZ2A%3D%3D; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; JSESSIONID=AD82F6571F45F22ED954637D2544CFCD; uc1="cookie15=URm48syIIVrSKA%3D%3D"; hng=CN%7Czh-CN%7CCNY%7C156; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; swfstore=139632; isg=BE9Pg1EfSPvgWUyAodhs6Gua3uP1Z_PKgT-6z2Fcyb7FMG4yaUXv550oNmCOSHsO',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',

}
def getEach():
    i = 0
    for data in document:
        i += 1
        _id = data['_id']
        url = data['url']
        canshu =  get_proKey(url)
        canshu['_id'] = _id
        db_list = db.products
        db_list.update_one({'_id': canshu['_id']}, {'$set': dict(canshu)}, upsert=True)
        print(_id,"---------"+str(i)+"page")
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
        # if len(open_duration)!=0:
        open_duration = "".join(open_duration)
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
        canshu = {'trading':trading,'count':count,'attribute':attribute,'open_duration':open_duration, 'production_date':production_date}
        return  canshu
    except Exception as e:
        print("detail-faild("+url+")", e)


if __name__ == "__main__":
    getEach()
    # Porducts()
    # get_proKey(url="https://detail.tmall.com/item.htm?id=571233457748&skuId=4611686589660845652&areaId=430100&user_id=509138323&cat_id=2&is_b=1&rn=d6198e62683be815cc6c8e841c211453")
    # get_proKey(url="https://detail.tmall.com/item.htm?id=540226087282&skuId=3202944271278&areaId=440300&user_id=2630035235&cat_id=2&is_b=1")