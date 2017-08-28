# coding:utf-8
from collections import defaultdict

import nltk
import wordcloud
import jieba
from matplotlib import pyplot as plt
import numpy as np
from scipy import stats
from gensim import similarities
from gensim.models import Word2Vec, LdaModel, LsiModel, tfidfmodel, RpModel, HdpModel
from gensim.models.word2vec import LineSentence
from gensim.corpora import Dictionary

import cleandata

class corpus(object):
    """
    use generator to pump one sentence one time,
    more memory-friendly
    """
    def __init__(self, filename=None):
        self.filename = filename
    def __iter__(self):
        try:
            for line in open(self.filename, 'r', encoding='utf-8', errors='ignore'):
                yield line.strip('\n').split(sep=" ")
        except FileNotFoundError:
            raise RuntimeError('Can not find file:{}'.format(self.filename))

class WordFreq(object):
    """
    use nltk and wordcloud to analysis the frequency of word in sentence
    """
    def __init__(self, commentlist=None, type='wordcloud'):
        """
        :param commentlist: a list object contained all comments in weibo
        :param type: the analysis method
        """
        self.commentlist = commentlist
        self.type = type

    def reconstructdata(self):
        """
        reconstruct data for different word frequency analysis
        :return: a dict object contained data
        """
        if self.type is 'wordcloud':
            print('starting to token...')
            cut_list = [list(jieba.cut(doc, cut_all=False)) for doc in self.commentlist]
            print('starting to wipe out stop words...')
            cut_list_nonstop = list(map(cleandata.remove_stop, cut_list))
            print('starting to join all words...')
            wordjoin =" ".join([word for sen in cut_list_nonstop for word in sen])
            result = {'type': self.type,
                      'result': wordjoin}
        elif self.type is 'freqdist':
            print('starting to token...')
            cut_list = [list(jieba.cut(doc, cut_all=False)) for doc in self.commentlist]
            print('starting to wipe out stop words...')
            cut_list_nonstop = list(map(cleandata.remove_stop, cut_list))
            print('starting to generate word list...')
            wordlist = [word for sen in cut_list_nonstop for word in sen]
            result = {'type': self.type,
                      'result': wordlist}
        else:
            result = None

        return result


    def drawcloud(self, width=800, height=600):
        """
        draw word cloud picture
        :param width: the width of picture
        :param height: the heigth of picture
        :return: the WordCloud object
        """
        wordjoin = WordFreq.reconstructdata(self)['result']
        wc = wordcloud.WordCloud(width=width, height=height)
        wc.generate(wordjoin)
        plt.imshow(wc)
        return wc

    def freqdist(self):
        """
        Calculate the frequency dist of a word list object
        :return: dict object, the summary of result
        """
        wordlist = WordFreq.reconstructdata(self)['result']
        wordfreq = nltk.FreqDist(wordlist)
        bins = wordfreq.B()
        all = wordfreq.N()
        most_common = wordfreq.most_common(100)
        summary = {'unique_words': bins,
                   'all_words': all,
                   'most_common': most_common}
        return summary

class WordVector(object):
    """

    """
    # TODO: 这个类用于生成语料的词向量并进行词语的相似性统计分析
    def __init__(self):
        import logging
        import multiprocessing
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
        logging.root.setLevel(level=logging.INFO)
        self.multi = multiprocessing.cpu_count()
        self.corpus = None


    def reconstructdata(self, commentlist=None, save=True, name='corpus.txt'):
        print('starting to token...')
        cut_list = [list(jieba.cut(doc, cut_all=False)) for doc in commentlist]
        print('starting to wipe out stop words...')
        cut_list_nonstop = list(map(cleandata.remove_stop, cut_list))
        cut_join = [" ".join(sentence) for sentence in cut_list_nonstop]
        print('合并列表至str，一共合并了{}个词'.format(len(cut_join)))
        join = "\n".join(cut_join)
        if save:
            with open(name, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(join)
                print('输出到文件：{}'.format(name))
                self.corpus = LineSentence(name)
                print('加载语料完成')
        else:
            return join


    def trainvector(self, save=True, savename=None):
        if not self.corpus:
            raise RuntimeError('use reconstructdata first to load corpus')
        model = Word2Vec(sentences=self.corpus, size=400, workers=self.multi)
        if save:
            print('输出词向量模型到文件：{}'.format(savename))
            model.wv.save_word2vec_format(savename)
        return model

    """
    需要进行句子相似性的分析，目前初步的算法思路是：
    1.获取标准情感词汇模板，如表示消极、积极、中性的词典
    2.将所有评论逐一与标准模板比较，计算相似性
    3.每个评论将会有三个标度的相似值：消极、积极、中性
    4.以此为依据来进行分类和打分
    """
class SenSimi(object):
    """
    This class can calculate the similarity of sentence
    """

    def __init__(self, cg=None):
        """
        initiate the class
        :param cg: the generator from class:Corpus
        """
        import logging
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
        logging.root.setLevel(level=logging.INFO)
        self.cg = cg
        self.bowlist = None
        self.word_dict = None


    def reconstructdata(self):
        """
        return word list and remove the word only appear 1 times
        :return: the word list after reconstruct
        """

        freq = defaultdict(int)
        print('generate freq list for every words.')
        for sentence in self.cg:
            for word in sentence:
                freq[word] += 1
        print('generating raw sentence...')
        raw = [[word for word in sentence if freq[word] > 1] for sentence in self.cg]
        return raw



    def bowcorpus(self, raw=None):
        """
        return the list of bag of words and buld dictionary
        :param raw: the raw list from reconstructdata
        :return: the list of bag of words
        """
        print('generating dictionary')
        self.word_dict = Dictionary(raw)
        print('generating the list of bow...')
        bowlist = [self.word_dict.doc2bow(sentence) for sentence in raw]
        self.bowlist = bowlist
        return bowlist

    def topicnum(self, n=None):
        """
        文档矩阵维度太大，需要舍弃那些tfidf太小的值来初步降低维度(特征数目），再进行主题数目分析
        也许需要降低文档数量，采用抽样法对小样本进行测试
        :return:
        """
        tfidfmodel = self.tfidfmodel(self.bowlist)
        corpus_tfidf = tfidfmodel[self.bowlist]
        try:
            corpus_tfidf_l = list(corpus_tfidf.__iter__())
        except MemoryError:
            raise RuntimeError('array is too big to operate.')
        print('using systematic sampling..')
        k = int(corpus_tfidf_l.__len__() / n)
        i = 0
        start = np.random.choice(n)
        sampler = []
        while sampler.__len__() < n:
            try:
                sampler.append(corpus_tfidf_l[start + i*k])
            except IndexError:
                sampler.append(corpus_tfidf_l[-1])
            i += 1
        sampler_tfidf_all = [word[1] for sen in sampler for word in sen]
        print('the length of sampler list :{}'.format(len(sampler)))
        fig = plt.hist(sampler_tfidf_all, 50, normed=True)
        plt.xlabel("TF-IDF")
        plt.ylabel("Probability Density")
        plt.show()



    def tfidfmodel(self, bowlist=None, save=False, savename=None):
        """
        tf-idf是tf和idf两个参数的乘积，tf（词频）表示某个词在一句话中出现的频率，如果一个词在
        一句话中多次出现，那么tf会是一个较大值
        idf（倒文档率）表示包含某个词的语句在整个语料库中所占比率倒数之对数值，如果一个词广泛出现在语料中，那么它的idf值会较小
        如果一个词在一句话中多次出现，但在整个语料中出现的不多，那么它一定对这句话很重要，所以它的tf-idf会较大
        build a tfidfmodel
        :param bowlist: the list of bag of words
        :param save: save the model
        :param savename: the file name of model
        :return: the model itself
        """
        print('using Tfidfmodel')
        tfidf = tfidfmodel.TfidfModel(bowlist)
        if save:
            print('输出TF-IDF模型到文件：{}'.format(savename))
            tfidf.save(savename)
        return tfidf
    def lsimodel(self, corpus_t=None, topic=200, save=False, savename=None):
        """

        :param tfidf:
        :param topic:
        :return:
        """
        print('using Lsimodel...')
        lsimodel = LsiModel(corpus=corpus_t, id2word=self.word_dict, num_topics=topic)
        if save:
            print('输出lsi模型到文件：{}'.format(savename))
            lsimodel.save(savename)
        return lsimodel

    def ldamodel(self, corpus_t=None, topic=200, save=False, savename=None):
        """

        :param tfidf:
        :param topic:
        :param save:
        :param savename:
        :return:
        """
        print('using Ldamodel...')
        ldamodel = LdaModel(corpus=corpus_t, id2word=self.word_dict, num_topics=topic)
        if save:
            print('输出lda模型到文件：{}'.format(savename))
            ldamodel.save(savename)
        return ldamodel

    def rpmodel(self, corpus_t=None, topic=200, save=False, savename=None):
        """

        :param corpus_t:
        :param topic:
        :param save:
        :param savename:
        :return:
        """
        print('using Random Projections model...')
        rpmodel =RpModel(corpus=corpus_t, id2word=self.word_dict, num_topics=topic)
        if save:
            print('输出rpm模型到文件：{}'.format(savename))
            rpmodel.save(savename)
        return rpmodel

    def hdpmodel(self, corpus_t, save=False, savename=None):
        """

        :param corpus_t:
        :param save:
        :param savename:
        :return:
        """
        print('using Hierarchical Dirichlet Process model...')
        hdpmodel = HdpModel(corpus=corpus_t, id2word=self.word_dict)
        if save:
            print('输出hdp模型到文件：{}'.format(savename))
            hdpmodel.save(savename)
        return hdpmodel
    def indexcompare(self, query=None, model=None, topic=200):

        tfidf_model = self.tfidfmodel(self.bowlist)
        corpus_tfidf = tfidf_model[self.bowlist]

        if model == 'lsi':
            vectorspace = self.lsimodel(corpus_t=corpus_tfidf, topic=topic)

        elif model == 'lda':
            # FIXME: very slow when generating index
            vectorspace = self.ldamodel(corpus_t=corpus_tfidf, topic=topic)
        elif model == 'rp':
            vectorspace = self.rpmodel(corpus_t=corpus_tfidf, topic=topic)
        elif model == 'hdp':
            vectorspace = self.hdpmodel(corpus_t=corpus_tfidf)
        else:
            raise RuntimeError('unrecognized model name')

        corpus_proj = vectorspace[corpus_tfidf]
        print('generating index matrix')
        corpus_index = similarities.MatrixSimilarity(corpus_proj, num_features=topic)

        query_bow = self.word_dict.doc2bow(query)
        query_tfidf = tfidf_model[query_bow]
        query_proj = vectorspace[query_tfidf]
        simi = corpus_index[query_proj]
        simi_list = list(simi)

        return simi_list

    def tfidfcurve(self):

        tfidfmodel = self.tfidfmodel(self.bowlist)
        corpus_tfidf = tfidfmodel[self.bowlist]
        #return corpus_tfidf
        try:
            corpus_tfidf_l = list(corpus_tfidf.__iter__())
            corpus_tfidf_v = [word[1] for sen in corpus_tfidf_l for word in sen]
            corpus_tfidf_v.sort()
        except MemoryError:
            raise RuntimeError('array is too big to operate.')
        #return corpus_tfidf_l
        y = np.array(corpus_tfidf_v)
        x = np.arange(len(y))
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.hist(y, bins=50, normed=True)
        ax1.set_xlabel('TF-IDF')
        ax1.set_ylabel('Probability Density')
        ax2.plot(x, y)
        ax2.set_xlabel('Words')
        ax2.set_ylabel('TF-IDF')
        fig.tight_layout()
        plt.show()


    def simihist(self, prob=True, bins=100, simi=None):

        num_bins = bins
        fig, ax = plt.subplots()

        n, bins, patches = ax.hist(simi, num_bins, normed=prob)

        print('starting Kernel density estimation....')
        kde = stats.gaussian_kde(simi)
        left = min(simi) - abs(0.5 * min(simi))
        right = 1.2
        x = np.arange(left, right, step=0.01)
        y = kde(x)
        ax.plot(x, y, '--')
        ax.set_xlabel('Similarity')
        ax.set_ylabel('Probability density')
        print('producing plot...')
        fig.tight_layout()
        plt.show()

















if __name__ == '__main__':

    #find = cleandata.dataloader('金丝猴', ('2016-01-01', '2016-03-31'))
    #res = cleandata.mergecomment(cursor=find, merge=False, punc=False)

    #wf = WordFreq(res, 'freqdist')
    #summary = wf.freqdist()
    #print(summary)
    #wv = WordVector('panda_cut_string.txt')
    #model = wv.train(save=True, savename='panda_nonstop_model.vector')
    #print(model.wv.most_similar('大熊猫'))
    FILENAME = 'panda_corpus.txt'
    panda_g = corpus(FILENAME)
    si = SenSimi(panda_g)
    panda_raw = si.reconstructdata()
    bowlist = si.bowcorpus(panda_raw)
    si.topicnum(600)
    si.tfidfcurve()
    tfidf = si.tfidfmodel(bowlist=si.bowlist, save=True, savename='panda_tfidf.model')
    panda_tfidf = tfidf[si.bowlist]
    cleandata.writepkl(panda_tfidf, 'panda_tfidf.matrix')

    # good = ['可爱', '萌', '喜欢', '国宝', '神奇']
    good = cleandata.loadpkl('moe_uni_t.pickle')
    bad = cleandata.loadpkl('bad_uni_t.pickle')
    """
    此处选择主题数目将直接影响simi表的结果，当主题数目很多时，相似性将很低
    当主题数目很少，相似性显著上升
    
    由于使用svd分解，需要找到一个合适的主题数目，该主题下还原得到的文档矩阵希望能和原来的矩阵差距较小
    有什么方法能够评价两个矩阵之间的相似程度？
    """

    res = si.indexcompare(query=good, model='rp', topic=50)
    cleandata.writepkl(res, 'panda_simi824.pickle')
    si.simihist(simi=res)

    #print(max(res))
    #print(len(res))


