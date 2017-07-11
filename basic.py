# coding:utf-8
import re
import yaml

from fake_useragent import UserAgent

with open('spiderconfig.yaml', 'r') as f:
    conf = f.read()
cf = yaml.load(conf)

LOGIN_URL = cf.get('URL')['login']
SEARCH_URL = cf.get('URL')['search']

def select_account(owner):
    try:
        account = cf.get(owner)['account']
        passwd = cf.get(owner)['passwd']
    except (TypeError, KeyError):
        raise RuntimeError('没有{}的账户信息'.format(owner))
    return (account, passwd)


def headers():
    """
    fake headers for requests session
    :return: a dic object, fake header
    """
    ua = UserAgent()
    headers = {
        'User-Agent':ua.random ,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    return headers

def is_login(source):
    """
    detect login status
    :param source:the html str object
    :return:boolean object
    """
    rs = re.search("CONFIG\['islogin'\](\s=\s|=)'(\d)'", source)
    if rs:
        return int(rs.group(2))==1
    else:
        return False

def is_person(source):
    """
    check this weibo  belong to a person account or a public account
    :param source: the html str objec
    :return: boolean object
    """
    rs = re.search("CONFIG\['domain'\](\s=\s|=)'(\d{1,7})'", source)
    if rs:
        return int(rs.group(2))==100505
    else:
        return False

def is_next(source):
    """
    check the search result page if it contains next page
    :param source: the search result html str object
    :return: boolean object
    """
    try:
        rs = re.search("page next S_txt1 S_line1", source)
    except TypeError:
        return ''
    if rs:
        return True
    else:
        return False




if __name__=='__main__':
    print(headers())