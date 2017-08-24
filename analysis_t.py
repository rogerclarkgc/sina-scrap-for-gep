from gensim import similarities
from gensim.models import LdaModel, LsiModel, tfidfmodel

from analysis import *

if __name__ == '__main__':

    FILENAME = 'panda_corpus.txt'

    panda_g = corpus(FILENAME)

    si = SenSimi(panda_g)

    panda_raw = si.reconstructdata()
    print(type(panda_raw))

    bowlist = si.bowcorpus(panda_raw)
    print(bowlist[1])

    panda_tfidfmodel = si.tfidfmodel(bowlist)
    panda_tfidf = panda_tfidfmodel[bowlist]
    # FIXME：不能用全部的语料生成索引，超出numpy.array限制
    # FIXME: 如果用部分语料，用于比较相似的句子不包括在索引矩阵的特征向量中（基）
    print('using lsi model...')
    panda_lsi = LsiModel(corpus=panda_tfidf, id2word=si.word_dict, num_topics=300)
    index = similarities.MatrixSimilarity(panda_lsi[panda_tfidf])
    good = ['可爱','萌', '喜欢','国宝','神奇']
    good_bow = si.word_dict.doc2bow(good)
    good_tfidf = panda_tfidfmodel[good_bow]
    good_lsi = panda_lsi[good_tfidf]
    simi = index[good_lsi]
    simi_list = list(simi)
    print(max(simi_list))
    where = simi_list.index(max(simi_list))
    print(panda_raw[where])
