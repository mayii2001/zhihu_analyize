'''
删除过少的文章和评论
评论单独当一篇document
先跑LDA看看
然后跑TF-IDF、TF-IWF、或改进长短句问题
'''
import json
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


def LDA_use(doc, num_topics):
    # 创建语料的词语词典，每个单独的词语都会被赋予一个索引
    dictionary = corpora.Dictionary(doc)
    # 使用上面的词典，将转换文档列表（语料）变成 DT 矩阵
    doc_term_matrix = [dictionary.doc2bow(d) for d in doc]
    # 保存到本地
    corpora.MmCorpus.serialize('corpus.mm', doc_term_matrix)
    # 使用 gensim 来创建 LDA 模型对象
    # 在 DT 矩阵上运行和训练 LDA 模型
    ldaModel = LDA.LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, alpha="auto", eta='auto', passes=10)
    topic_list = ldaModel.print_topics(num_topics, 10)
    print("主题的单词分布为：\n")
    for topic in topic_list:
        print(topic)
    return ldaModel, dictionary


if __name__ == '__main__':
    with open('SplitedAnswers.json', encoding='utf-8') as j:
        j = json.load(j)
    text = [i['text'] for i in j]

    a = range(1, 20, 1)  # 主题个数
    p = []
    for num_topics in a:
        lda, dictionary = LDA_use(text, num_topics)
        corpus = corpora.MmCorpus('corpus.mm')
        prep = perplexity(lda, corpus, dictionary, len(dictionary.keys()), num_topics)
        p.append(prep)

    graph_draw(a, p)
