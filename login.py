# coding:utf-8
import time
import re
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions as CEC
from bs4 import BeautifulSoup

import basic

def login_sina(account, password, url):
    # initiate driver
    retry_login = 3
    retry_submit = 3
    print('初始化PhantomJS...\n')
    driver = webdriver.Chrome()
    #driver = webdriver.Chrome()
    driver.maximize_window()
    # load login page
    print('加载登陆页面...\n')
    while retry_login > 0:
        try:
            # 由于网络问题，driver.get()花费时间较长
            # FIXME: 可能由于weibo包含过多动态加载内容，几乎所有的提交操作反应都很慢
            driver.get(url)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'loginname')))
            break
        except CEC.TimeoutException:
            retry_login -= 1
            print('加载登陆页面失败，还剩%d次重试\n' % (retry_login))
            time.sleep(5)
        finally:
            print(driver.title, '\n')
    if retry_login <= 0:
        raise RuntimeError('无法加载登陆页面,程序退出！\n')
    print('开始登陆...\n')
    # find account frame
    name_field = driver.find_element_by_id('loginname')
    name_field.clear()
    name_field.send_keys(account)
    # find password frame
    password_field = driver.find_element_by_class_name('password').find_element_by_name('password')
    password_field.clear()
    password_field.send_keys(password)
    # find login button
    submit = driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a/span')
    while retry_submit > 0:
        try:
            #submit.click()
            ActionChains(driver).double_click(submit).perform()
            time.sleep(15)
            # check the elements in the page, if contains the user's nick name, continue to next steps
            # FIXME: 会出现明明已经成功加载个人主页，但WebDriverWait仍然判断没有成功加载的情况
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'WB_miniblog')))
            source = driver.page_source
            if basic.is_login(source=source):
                print('登陆成功\n')
                break
            else:
                retry_submit -= 1
                print('登陆信息没有成功提交，还有%d次重试,8秒后开始\n' % retry_submit)
                time.sleep(5)
        except CEC.TimeoutException:
            print('登陆失败！等待时间超过设定值\n进行下一次重试\n')
            retry_submit -= 1
            time.sleep(5)
        finally:
            print(driver.title, '\n')
        if retry_submit <= 0:
            raise RuntimeError('无法登陆，程序退出!')
    #ActionChains(driver).double_click(submit).perform()
    sina_cookies = driver.get_cookies()
    print('输出到图片\n')
    driver.save_screenshot('weibo.jpg')
    print('关闭webdriver...')
    driver.close()
    return sina_cookies


if __name__ == '__main__':
    url = basic.LOGIN_URL
    name_input = basic.ACOUNT
    passwd_input = basic.PASSWD
    cookies = login_sina(name_input, passwd_input, url)
    #pprint(cookies)
    #print(type(cookies), len(cookies))


