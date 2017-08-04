# coding:utf-8
import time
import re
import random
from datetime import datetime, timedelta, date
from calendar import monthrange
import yaml

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

with open('D:\\work\\python\sina-scrap-for-gep\\spiderconfig.yaml', 'r') as f:
    conf = f.read()
cf = yaml.load(conf)

page_gap = cf.get('config')['page_gap']
person_gap_min = cf.get('config')['person_gap_min']
person_gap_max = cf.get('config')['person_gap_max']

def first_login(owner='xie'):
    print('开始首次登陆新浪微博，使用的账户为{}'.format(owner))
    cookies = login_sina(owner, basic.LOGIN_URL)
    print('开始添加cookies到数据库')
    status = add_cookies(cookies, owner)
    print('插入状态是：{}\n等待5秒...'.format(status))
    time.sleep(5)
    f_cookies = fetch_cookies(owner)
    print('检测cookies可用性')
    res = check_cookie(f_cookies, basic.SEARCH_URL)
    print('检测结果：{}'.format(res))

def search_task(keyword, start, end, owner='xie', start_page=1, first=False):
    error = []
    if first:
        first_login()
    next_page = True
    start_page = start_page
    while next_page:
        retrysearch = 3
        print('##############开始获取：第{}页搜索结果##############'.format(start_page))
        print('###等待6秒...###')
        search_page = get_search_page(keyword=keyword,
                                      start=start,
                                      end=end,
                                      page=start_page,
                                      owner=owner)
        # FIXME:由于未知原因，搜索链接会搜索不到结果，导致search_result为None
        search_result = html_screen.get_search_result(search_page)
        next_page = basic.is_next(search_result)
        if next_page == '':
            while next_page == '':
                if retrysearch > 0:
                    print('###未出现搜索结果，开始重试搜索###\n###等待10秒###\n')
                    time.sleep(10)
                else:
                    print('###3次搜索失败，开始一次长时间静默\n###等待45秒###\n')
                    time.sleep(45)
                    retrysearch = 3
                search_page = get_search_page(keyword=keyword,
                                              start=start,
                                              end=end,
                                              page=start_page,
                                              owner=owner)
                search_result = html_screen.get_search_result(search_page)
                next_page = basic.is_next(search_result)
                retrysearch-=1
        print('###下一页：{}###'.format(next_page))
        start_page += 1
        weibo = Weibo(search_result)
        weibo_info = WeiboInfo(search_result)
        weibo_list = weibo.get_weibo()
        weibo_info_list = weibo_info.get_weibo_info()
        print('###开始获取博主个人信息###')
        for index, weibo in enumerate(weibo_list):
            # set the time gap of crawling
            wait = random.randint(person_gap_min, person_gap_max)
            choice = random.choice(['roger', 'towa', 'xie'])
            user_id = weibo['user_id']
            print('###等待{}秒...###'.format(wait))
            #print('###comment:{}###\n###user:{}###'.format(weibo['comment'], weibo['nick_name']))
            time.sleep(wait)
            print('###选择{}的账户进行登录###'.format(choice))
            print('###获取的博主id为{}, 这是第{}个微博'.format(user_id, index+1))
            user_page = get_user_page(user_id, choice)
            user_content = html_screen.get_personal_result(user_page)
            person = PersonalInfo(user_content)
            all_info = person.get_all_info()
            weibo['personinfo'] = all_info

        full_weibo = html_screen.reconstruct_weibo(weibo_list, weibo_info_list, keyword)
        count = store_task(full_weibo)
        error.append(count)
        print('###插入操作，成功：{}，失败：{}###'.format(len(full_weibo)-len(count), len(count)))
    print('##############结束获取##############')
    return error

def one_year(year=None, month=(1, 12), keyword=None, ownerlist=None, waite=None):
    """
    apply search_task for one year
    :param year: the int number of year
    :param month: the month int value
    :param keyword: the serach key word
    :param ownerlist: a list object to store cookies'owners
    :param waite:the waite time for every month
    """
    all = range(month[0], month[1]+1)
    print('###开始获取第{}的搜索结果，开始月份：{}'.format(year, month))
    for month in all:
        stop = monthrange(year, month)[1]
        startday = '{}-{}-01'.format(year, month)
        stopday = '{}-{}-{}'.format(year, month, stop)
        ow = random.choice(ownerlist)
        error_month = search_task(keyword=keyword,
                                  owner=ow,
                                  start=startday,
                                  end=stopday,
                                  start_page=1)
        print(error_month)
        #print('startday:{},\n stopday:{}'.format(startday, stopday))
        print('###已完成{}年的获取任务，暂停{}秒###'.format(year, waite))
        time.sleep(waite)

def store_task(weibo_list=None):
    errorlist = []
    storer = database.DataBase()
    print('###一共有{}条微博将插入数据库###'.format(len(weibo_list)))
    count = 0
    for weibo in weibo_list:
        error = storer.addin(weibodict=weibo, check_mode=False)
        if len(error) == 0:
            count += 1
        else:
            errorlist.append(error)
    storer.close()
    return errorlist
# TODO: 可以加入多进程系统，并发多线程操作


if __name__ == '__main__':

    #ow = random.choice(['roger', 'towa', 'xie'])
    ownerlist = ['roger', 'towa', 'xie']
    one_year(year=2015,
             month=(1,6),
             keyword='金丝猴',
             ownerlist=ownerlist,
             waite=basic.MONTH_GAP
             )
 
