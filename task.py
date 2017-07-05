# coding:utf-8
import time
import re
import random
from datetime import datetime, timedelta, date

import basic
from login import  login_sina
from cookies import fetch_cookies, check_cookie, add_cookies
from fetch_page import get_search_page, get_user_page
from html_screen import Weibo, WeiboInfo, PersonalInfo
import html_screen
import database

"""
这个模块将用于实际的爬取操作
"""
# TODO: 爬取流程实现：1.初步登陆 2.获取搜索关键词 3.执行搜索 4.获取搜索页面 5. 抓取页面数据 6.存储数据到数据库
# TODO: 爬虫复用流程实现：1.对搜索结果是否有下一页判断 2.设定爬取间断值以防止封号

def first_login():
    print('开始首次登陆新浪微博，使用的账户为{}'.format(basic.ACOUNT))
    cookies = login_sina(basic.ACOUNT, basic.PASSWD, basic.LOGIN_URL)
    print('开始添加cookies到数据库')
    status = add_cookies(cookies, 'roger')
    print('插入状态是：{}\n等待5秒...'.format(status))
    time.sleep(5)
    f_cookies = fetch_cookies('roger')
    print('检测cookies可用性')
    res = check_cookie(f_cookies, basic.SEARCH_URL)
    print('检测结果：{}'.format(res))

def search_task(keyword, start, end, cookie_owner='roger', first=False):
    if first:
        first_login()
    next_page = True
    start_page = 1
    while next_page:
        search_page = get_search_page(keyword=keyword,
                                      start=start,
                                      end=end,
                                      page=start_page)
        search_result = html_screen.get_search_result(search_page)
        weibo = Weibo(search_result)
        weibo_info = WeiboInfo(search_result)
        weibo_list = weibo.get_weibo()
        weibo_info_list = weibo_info.get_weibo_info()
        re_weibo = html_screen.reconstruct_weibo(weibo_list, weibo_info_list)




if __name__ == '__main__':
    first_login()
