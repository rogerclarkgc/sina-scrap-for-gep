# coding:utf-8
import time
from datetime import time, datetime, timedelta, date

import pymongo
import requests

import basic
from login import login_sina
# TODO: store cookies in mongodb
# TODO: fetch cookies from mongodb
# TODO: check cookies' usability

def add_cookies(cookies, name):
    """
    add cookies in mongodb
    :param cookies: a list object contained cookies
    :param name: the name of cookies' owner
    :return:the status of insert operation
    """
    # initializing a MongoClient
    client = pymongo.MongoClient()
    db = client.sina
    collection = db.cookies
    # test connection
    if collection.find_one({'test':'ok'}):
        print('已连接Mongodb!, collection:cookies')
        if len(cookies) <= 0:
            print('没有要插入的cookies')
            status = 'N_COOKIE'
        else:
            print('开始插入操作')
            time = datetime.now().strftime('%Y-%m-%d %X')
            for cookie in cookies:
                cookie['insert_time'] = time
                cookie['owner'] = name
                message = collection.insert_one(cookie)
            print("插入%d条cookies到数据库，属于用户%s" % (len(cookies), name))
            status = 'INSERT_OK'
    else:
        status = 'N_CONNECT'
    client.close()
    return status

def fetch_cookies(owner, name='SUB', date=None):
    """

    :param owner: the cookies' owner
    :param date: the cookies date(%Y-%m-%d), if not assign, use the latest cookie in the database
    :param name: the cookies key, default assignment is 'SUB'
    :return:reconstruct cookies
    """
    # TODO: fetch and reconstruct cookies from mongodb
    client = pymongo.MongoClient()
    db = client.sina
    collection = db.cookies
    if collection.find_one({'test':'ok'}):
        print('已连接Mongodb!')
        if date:
            period = timedelta(days=1)
            date_r = datetime.strptime(date, '%Y-%m-%d')
            date_r = (date_r + period).strftime('%Y-%m-%d')
            cursor = collection.find({'name': name,
                                      'owner': owner,
                                      'insert_time':{'$lt':date_r}})
            try:
                cookie = next(cursor.sort('insert_time', pymongo.DESCENDING))
            except StopIteration:
                raise RuntimeError('没有找到名字为%s, 拥有者为%s, 日期为%s的cookie'% (name, owner, date))
        else:
            cursor = collection.find({'name':name, 'owner':owner})
            try:
                cookie = next(cursor.sort('insert_time', pymongo.DESCENDING))
            except StopIteration:
                raise RuntimeError('没有找到名字为%s, 拥有者为%s的cookie' % (name, owner))
        r_cookies = {cookie['name']: cookie['value']}
        print('获取的cookies的时间是%s, 拥有者为%s' % (cookie['insert_time'], owner))
    else:
        raise RuntimeError('没有成功连接到数据库，程序终止!')
    client.close()
    return r_cookies

def check_cookie(cookie_dict, url):
    # TODO: check cookie is available for login
    """

    :param cookie_dict: a cookie dict to use in a requests session
    :param url: target website
    :return: status code
    """
    s = requests.Session()
    page = s.get(url=url, cookies=cookie_dict, headers=basic.headers())
    check = basic.is_login(page.text)
    s.close()
    return check


if __name__ == '__main__':

    cookies = login_sina('xie', basic.LOGIN_URL)
    status = add_cookies(cookies, 'xie')
    print(status)

    f_cookie = fetch_cookies('xie')
    print(f_cookie)
    print(check_cookie(f_cookie, basic.SEARCH_URL))




