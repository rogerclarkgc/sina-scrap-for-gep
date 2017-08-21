# coding:utf-8
import nltk
import wordcloud
import jieba
from matplotlib import pyplot as plt

import cleandata

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
        reconstruct data
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
        if self.type is 'freqdist':
            print('starting to token...')
            cut_list = [list(jieba.cut(doc, cut_all=False)) for doc in self.commentlist]
            print('starting to wipe out stop words...')
            cut_list_nonstop = list(map(cleandata.remove_stop, cut_list))
            print('starting to generate word list...')
            wordlist = [word for sen in cut_list_nonstop for word in sen]
            result = {'type': self.type,
                      'result': wordlist}

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

if __name__ == '__main__':

    find = cleandata.dataloader('金丝猴', ('2016-01-01', '2016-03-31'))
    res = cleandata.mergecomment(cursor=find, merge=False, punc=False)

    wf = WordFreq(res, 'freqdist')
    summary = wf.freqdist()
    print(summary)


