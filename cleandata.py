# coding:utf-8
import string
import re
import textwrap

def cleancomment(comment=None):
    """
    clean the comment, remove non chinese characters(punctuation is not included)
    :param comment:the comment string
    :return:string object, the comment after cleaning
    """
    # basic chinese characters and punctuations
    pattern = '[\u4e00-\u9fa5,。,，,！,？,：,、]'
    result = re.findall(pattern, comment)
    if len(result)==0:
        return ''
    else:
        clean = "".join(result)
        return clean

def writepkl(splitword=None):
    pass




