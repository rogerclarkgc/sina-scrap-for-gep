# coding:utf-8
from login import login_sina
from selenium.common.exceptions import WebDriverException
from selenium import webdriver

import time
from pprint import pprint

import basic
"""
test cookies
"""


def test_cookies(cookies, url):
    useful_cookie = []
    print('There are %d cookies in the list' %(len(cookies)))
    for index, cookie in enumerate(cookies):
        print('Start test NO.%d cookie' %(index))
        print('''The name of cookie: %s
        The value of cookie: %s''' %(cookie['name'], cookie['value']))
        try:
            print('initiate PhantomJS...')
            driver = webdriver.PhantomJS()
            print('add cookie...')
            driver.add_cookie(cookie)
        except WebDriverException:
            print('can not load this cookie into driver!')
        finally:
            driver.get(url)
            time.sleep(12)
            if basic.is_login(driver.page_source):
                print('Login successful!')
                useful_cookie.append(cookie)
            else:
                print('Login failure!')
            driver.delete_all_cookies()
            driver.close()
            time.sleep(5)
    return  useful_cookie

if __name__ == '__main__':
    print('starting get cookies')
    cookies = login_sina(basic.ACOUNT, basic.PASSWD, basic.LOGIN_URL)

    useful_cookies = test_cookies(cookies, basic.LOGIN_URL)
    pprint(useful_cookies)