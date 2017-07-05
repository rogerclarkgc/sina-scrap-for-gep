# coding:utf-8
import time
from datetime import time, datetime, timedelta, date

from pymongo import MongoClient
"""
这个模块用于进行微博内容存储与读取的操作
"""
# TODO: 组织好的微博数据存入数据库。
# TODO: 提取数据库中的数据
# TODO: 存储前查询数据是否存在

class DataBase(object):
    def __init__(self):
        self.client = MongoClient()
        self.sinadb = self.client.sina
        self.weibocol = self.sinadb.weibo
        self.status = 'INITIATE'
        if self.weibocol.find_one({'test':'ok'}):
            print('已连接Mongodb, collection:weibo')
            self.status = 'CONNECTED'
        else:
            self.status = 'FAILURE_MONGODB'

    def addin(self, weibodict, check_mode=False):
        if check_mode is True:
            if self.check(weibodict['i_stamp']) is True:
                print('发现重复数据，不执行插入')
                return self.status
            else:
                pass
        else:
            pass
        message = self.weibocol.insert_one(weibodict)
        strnow = datetime.now().strftime('%Y-%m-%d %X')
        if message._WriteResult_acknowledged:
            print('已插入微博数据到数据库，集合：weibo，插入时间为：{}'.format(strnow))
            self.status = 'INSERT_OK'
        else:
            print('插入操作失败，集合：weibo，插入时间为：{}'.format(strnow))
            self.status = 'INSERT_FAILURE'
        return self.status

    def fetch(self, **kwargs):
        pass

    def check(self, stamp=None):
        res = self.weibocol.find_one({'i_stamp':stamp})
        if res:
            return True
        else:
            return False

    def delete(self, **kwargs):
        pass
