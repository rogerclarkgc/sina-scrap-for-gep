# coding:utf-8
import string
import re
import textwrap
import pickle

from tqdm import tqdm
import jieba



from pymongo import MongoClient


def cleancomment(comment=None, punctuation=True):
    """
    clean the comment, remove non chinese characters
    :param punctuation:boolean value, if True, will not exclude punctuation
    :param comment:the comment string
    :return:string object, the comment after cleaning
    """
    # basic chinese characters and punctuations
    pattern = '[\u4e00-\u9fa5]'
    if punctuation:
        pattern = '[\u4e00-\u9fa5,。,，,！,？,：,、]'
    other = ['网页链接', '秒拍视频', '展开全文']
    for i in other:
        if i in comment:
            comment = comment.replace(i, '')
        else:
            continue
    result = re.findall(pattern, comment)
    if len(result)==0:
        return ''
    else:
        clean = "".join(result)
        return clean
def remove_stop(cutlist=None, stopword=None):
    """

    :param cutlist:the cut list of an comment
    :param stopword:the list of stop word
    :return:
    """
    if not stopword:
        #print('使用自建词典...')
        stopdic = loadpkl('stop_list.pickle')
    else:
        #print('使用用户提供词典...')
        stopdic = stopword
    nonstop = [word for word in cutlist if word not in stopdic]
    return nonstop



def mergecomment(cursor=None, merge = False, split='\n', punc = False):
    """
    merge all comment in one string object
    :param cursor: pymongo cursor object
    :param merge: merge all doc in one string object
    :param split: the split character of every comment
    :param punc: if true, will not exclude punctuations in comments
    :return: the string object or list object
    """
    result = None
    print('当前cursor中的文档数目为：{}'.format(cursor.count()))
    print('开始执行文档合并操作，分隔符号为：{}'.format(split))
    result = [cleancomment(doc['comment'], punctuation=punc) for doc in cursor]
    print('合并完成！')
    if merge:
        return split.join(result)
    else:
        return result

def wordjoin(cutlist=None, sep=" "):
    """
    use sep to link all sentence in cut list
    :param cutlist: the list of cut result for every sentence
    :param sep: the character to seperate every word
    :return:the str object
    """
    join = sep.join([sep.join(cut) for cut in cutlist])
    return join

def writepkl(doc=None, name='data.pickle'):
    """
    write .pickle files in work directory
    :param doc:object to store
    :param name:the name of files
    :return: None
    """
    with open(name, 'wb') as f:
        pickle.dump(doc, f, pickle.HIGHEST_PROTOCOL)

def loadpkl(name='data.pickle'):
    """
    load .pickle file from work directory
    :param name:the filename of .pickle
    :return:the object in .pickle
    """
    with open(name, 'rb') as f:
        data = pickle.load(f)
    return data

def writetxt(name='corpus.txt', doc=None):
    if isinstance(doc, str) is False:
        raise RuntimeError('doc need be a str object')
    else:
        with open(name, 'r', encoding='utf-8', errors='ignore') as f:
            f.write(doc)
            return 1

def dataloader(keyword, timegap=None):
    """
    find raw data from mongodb
    :param keyword: the keyword of comment
    :param timegap: time gap of comment, ('2017-01-01', '2017-01-31')
    :return: the cursor of database
    """
    db = MongoClient()
    col = db.sina.weibo
    if not timegap:
        query = {'keyword':keyword}
        find = col.find(query)
    else:
        query = {'keyword': keyword,
                 'timestamp': {'$gte': timegap[0],
                               '$lte': timegap[1]}}
        find = col.find(query)
    return find

if __name__ == '__main__':

    db = MongoClient()
    col = db.sina.weibo
    find = col.find({'keyword':'大熊猫'})
    print('starting to merge...')
    res = mergecomment(cursor=find, merge=False, split="", punc = False)

    print('start to token...')
    cut_list = [list(jieba.cut(doc, cut_all=False)) for doc in res]

    print('starting to wipe out stop words...')
    cut_list_nonstop = list(map(remove_stop, cut_list))

    print('write result list')
    writepkl(res, name='panda_raw_list.pickle')
    writepkl(cut_list, name='panda_cut_list.pickle')
    writepkl(cut_list_nonstop, name='panda_cut_nonstop.pickle')



