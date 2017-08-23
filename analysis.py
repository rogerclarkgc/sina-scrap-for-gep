# coding:utf-8
from collections import defaultdict

import nltk
import wordcloud
import jieba
from matplotlib import pyplot as plt
from gensim import similarities
from gensim.models import Word2Vec, LdaModel, LsiModel, tfidfmodel
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

    def __init__(self, cg=None):
        import logging
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
        logging.root.setLevel(level=logging.INFO)
        self.cg = cg
        self.word_dict = None


    def reconstructdata(self):

        freq = defaultdict(int)
        print('generate freq list for every words.')
        for sentence in self.cg:
            for word in sentence:
                freq[word] += 1
        print('generating raw sentence...')
        raw = [[word for word in sentence if freq[word] > 1] for sentence in self.cg]
        return raw

    def bowcorpus(self, raw=None):
        print('generating dictionary')
        self.word_dict = Dictionary(raw)
        print('generating the list of bow...')
        bowlist = [self.word_dict.doc2bow(sentence) for sentence in raw]
        return bowlist

    def tfidfmodel(self, bowlist=None, save=False):
        print('using Tfidfmodel')
        tfidf = tfidfmodel.TfidfModel(bowlist)
        return tfidf












if __name__ == '__main__':

    #find = cleandata.dataloader('金丝猴', ('2016-01-01', '2016-03-31'))
    #res = cleandata.mergecomment(cursor=find, merge=False, punc=False)

    #wf = WordFreq(res, 'freqdist')
    #summary = wf.freqdist()
    #print(summary)
    wv = WordVector('panda_cut_string.txt')
    model = wv.train(save=True, savename='panda_nonstop_model.vector')
    print(model.wv.most_similar('大熊猫'))


