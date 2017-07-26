# coding:utf-8
import time
import re
import random
from urllib import parse

import requests
from bs4 import BeautifulSoup

from login import login_sina
import basic
from basic import headers
from cookies import add_cookies, fetch_cookies, check_cookie

def get_page(url, login=True, retry=3, owner=None):
    """
    get basic html page
    :param url: the url of html page
    :param login: if need login
    :param retry: the num of retry when error occured
    :param owner: the cookies' owner
    :return: the string object of html
    """
    count = 0
    while count < 3:
        if login:
            print('此次抓取需要登录\n获取{}的COOKIES中...'.format(owner))
            # TODO: need to store cookies in a file or database
            cookie = fetch_cookies(owner)
        try:
            session = requests.Session()
            if login:
                print('开始获取页面...')
                paraset = {'url': url,
                           'headers': headers(),
                           'cookies': cookie}

                weibo = basic.timelimit(10, session.get, kwargs=paraset)

                page = weibo.text
                if basic.is_login(page):
                    print('抓取{}页面成功'.format(url))
                    return page
                else:
                    # TODO: 需要一个切换owner的方法
                    #ownerpool = ['roger', 'xie']
                    #return get_page(owner=)
                    raise RuntimeError('属于用户{}的cookies可能失效'.format(owner))
            else:
                weibo = session.get(url=url,
                                    headers=headers())
                page = weibo.text
                return page
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, AttributeError, TimeoutError) as e:
            count+=1
            print('爬取{}出现错误，错误原因是{}\n开始第{}次爬取'.format(url, e, count+1))
            time.sleep(random.randint(5, 15))

    print('爬取{}已到最大重试次数，爬取失败!'.format(url))
    return 'FAILURE_CRAWLING'

def get_search_page(keyword, start, end, page, owner):
    """
    get result of search page
    :param keyword: the keyword for search
    :param start:the start time interval of search
    :param end:the end time interval of search
    :param page:the page number of search result
    :param owner: the cookies' owner
    :return: the string object of html page
    """
    # scope=ori:原创
    # timescope: 时间区间，必须是'%Y-%m-%d'的格式
    base_url = 'http://s.weibo.com/weibo/{}&scope=ori&suball=1&timescope=custom:{}:{}&page={}'
    kq = parse.quote(parse.quote(keyword))
    base_url = base_url.format(kq, start, end, page)
    result = get_page(base_url, owner=owner)
    return result

def get_user_page(user_id, owner):
    """
    get a user's personal info page
    :param user_id: the weibo id of user, 'user_id'
    :param owner: the cookies' owner
    :return: the page of personal info or 'PUBLIC_ACCOUNT' for public account
    """
    # TODO: 需要再抓取个人信息前判断当前请求的是一个个人主页
    base_url = 'http://weibo.com/p/100505{}/info?mod=pedit_more'.format(user_id)
    result = get_page(base_url, owner=owner)
    if basic.is_person(result):
        return result
    else:
        return 'PUBLIC_ACCOUNT'


if __name__ == '__main__':
    #page = get_page(url=basic.SEARCH_URL)

    #print(page)
    #print(basic.is_login(page))
    r = get_search_page(keyword='大熊猫',
                        start='2017-1-1',
                        end='2017-6-29',
                        page=1,
                        owner='xie')
    #r.encode()
    fp = open('search_result.html', 'w', encoding='utf8')
    fp.write(r)
    fp.close()