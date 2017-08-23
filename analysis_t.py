from gensim import similarities

from analysis import *

if __name__ == '__main__':

    FILENAME = 'panda_corpus.txt'

    panda_g = corpus(FILENAME)

    si = SenSimi(panda_g)

    panda_raw = si.reconstructdata()
    print(type(panda_raw))

    bowlist = si.bowcorpus(panda_raw)
    print(bowlist[1])

    panda_tfidf = si.tfidfmodel(bowlist)
    # FIXME：不能用全部的语料生成索引，超出numpy.array限制
    # FIXME: 如果用部分语料，用于比较相似的句子不包括在索引矩阵的特征向量中（基）
    panda_res = panda_tfidf[bowlist[:2]]
    index = similarities.MatrixSimilarity(panda_res)

    good = ['可爱','萌', '喜欢','国宝','神奇']
    good_bow = si.word_dict.doc2bow(good)
    good_tfidf = panda_tfidf[good_bow]
    simi = index[good_tfidf]
    simi_list = list(simi)
    print(max(simi_list))
    print(good_tfidf)
    print(good_bow)