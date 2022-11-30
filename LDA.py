'''
删除过少的文章和评论
评论单独当一篇document
先多进程跑LDA看看
然后跑TF-IDF、TF-IWF、或改进长短句问题
'''
import json
from concurrent.futures import ProcessPoolExecutor
from gensim import corpora
from matplotlib import pyplot as plt
import gensim.models.ldamodel as LDA
import math


def perplexity(trainedModel, testset, dictionary, size_dictionary, num_topics):
    print('the info of this ldamodel: ')
    print('  num of topics: %s' % num_topics)
    prep = 0.0
    prob_doc_sum = 0.0
    topic_word_list = []
    for topic_id in range(num_topics):
        topic_word = trainedModel.show_topic(topic_id, size_dictionary)
        dic = {}
        for word, probability in topic_word:
            dic[word] = probability
        topic_word_list.append(dic)
    doc_topics_ist = []
    for doc in testset:
        doc_topics_ist.append(trainedModel.get_document_topics(doc, minimum_probability=0))
    testset_word_num = 0
    for i in range(len(testset)):
        prob_doc = 0.0  # the probablity of the doc
        doc = testset[i]
        doc_word_num = 0
        for word_id, num in dict(doc).items():
            prob_word = 0.0
            doc_word_num += num
            word = dictionary[word_id]
            for topic_id in range(num_topics):
                # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                prob_topic = doc_topics_ist[i][topic_id][1]
                prob_topic_word = topic_word_list[topic_id][word]
                prob_word += prob_topic * prob_topic_word
            prob_doc += math.log(prob_word)  # p(d) = sum(log(p(w)))
        prob_doc_sum += prob_doc
        testset_word_num += doc_word_num
    prep = math.exp(-prob_doc_sum / testset_word_num)  # perplexity = exp(-sum(p(d)/sum(Nd))
    print("  模型困惑度的值为 : %s" % prep)
    return prep


def graph_draw(topic, perplexity):  # 做主题数与困惑度的折线图
    x = topic
    y = perplexity
    plt.plot(x, y, color="red", linewidth=2)
    plt.xlabel("Number of Topic")
    plt.ylabel("Perplexity")
    plt.show()


def createCorpus(doc):
    # 创建语料的词语词典，每个单独的词语都会被赋予一个索引
    dictionary = corpora.Dictionary(doc)
    dictionary.save('LDAmodel/Z_A.dict')
    # 使用上面的词典，将转换文档列表（语料）变成 DT 矩阵
    doc_term_matrix = [dictionary.doc2bow(d) for d in doc]
    # 保存到本地
    corpora.MmCorpus.serialize('LDA\corpus.mm', doc_term_matrix)
    return dictionary, doc_term_matrix


def LDA_use(dictionary, doc_term_matrix, num_topics):
    # 使用 gensim 来创建 LDA 模型对象
    # 在 DT 矩阵上运行和训练 LDA 模型
    ldaModel = LDA.LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, alpha="auto", eta='auto',
                            passes=30)
    topic_list = ldaModel.print_topics(num_topics, 10)
    # print("主题的单词分布为：\n")
    # for topic in topic_list:
    #     print(topic)
    return ldaModel


def multi_LDA_P(args):
    num_topics = args
    lda = LDA_use(dic, DT, num_topics)
    corpus = corpora.MmCorpus("corpus.mm")
    p = perplexity(lda, corpus, dic, len(dic.keys()), num_topics)
    print(p)
    return p


with open('data/SplitedAnswers_Comments_Q.json', encoding='utf-8') as j:
    j = json.load(j)
text = [i['text'] for i in j]
for i in j:
    for c in i['comment']:
        text.append(c['content'])
dic, DT = createCorpus(text)  # 全局变量

if __name__ == '__main__':

    a = range(1, 30, 1)  # 主题个数
    allp = []
    # 多进程加速
    with ProcessPoolExecutor(13) as p:
        try:
            results = p.map(multi_LDA_P, a)
            # 按a的顺序返回
            for r in results:
                allp.append(r)
        except Exception as e:
            print(e)
        # jobs=[p.submit(multi_LDA_P, [text, i]) for i in a]
        # for job in jobs:
        #     allp.append(job.result())
    p.shutdown(wait=True)
    graph_draw(a, allp)
    print(allp)
