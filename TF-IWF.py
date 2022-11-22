#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/3 12:31
# @Author  : mokundong

import math
import numpy as np


class TF_IWF:
    '''
    tf-iwf 算法
    '''

    def __init__(self, lines):
        self.iwf = dict()
        self.median_iwf = 0
        self.__build_iwf(lines)

    def __get_tf(self, strs):
        tf_dict = {}
        line_words = strs.split(" ")
        total_word_line = len(line_words)
        for word in line_words:
            if word not in tf_dict:
                tf_dict[word] = 1
            else:
                tf_dict[word] = tf_dict[word] + 1
        for k, v in tf_dict.items():
            tf_dict[k] = v / total_word_line
        return tf_dict

    def __build_iwf(self, lines):

        for line in lines:
            line_words = line.split(" ")
            for word in line_words:
                if word not in self.iwf:
                    self.iwf[word] = 1
                else:
                    self.iwf[word] = self.iwf[word] + 1
        total_word_lines = len(self.iwf.values())
        values = []
        for k, v in self.iwf.items():
            self.iwf[k] = math.log(total_word_lines / v, 10)
            values.append(math.log(total_word_lines / v, 10))
        self.median_iwf = np.median(values)

    def get_tfiwf(self, strs):
        result = dict()
        tf_dict = self.__get_tf(strs)
        line_words = strs.split(" ")
        for word in line_words:
            if word not in self.iwf.keys():
                result[word] = tf_dict[word] * self.median_iwf
            else:
                result[word] = tf_dict[word] * self.iwf[word]
        return result


if __name__ == "__main__":
    lines = [
        '这是 第一 篇 文章 ',
        '这 篇 文章 是 第二 篇 文章 ',
        '这是 第三 篇 文章 '
    ]
    line = '这是 第几 篇 文章'
    tfiwf = TF_IWF(lines)
    result = tfiwf.get_tfiwf(line)
    print(result)

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # @Time    : 2019/10/30 09:48
    # @Author  : mokundong
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer

    x_train = ['这是 第一 篇 文章 ，',
               '这 篇 文章 是 第二 篇 文章 。',
               '这是 第三 篇 文章 。'
               ]
    x_test = ['这是 第几 篇 文章 ？']
    CV = CountVectorizer(max_features=10)
    transformer = TfidfTransformer()
    tf_idf = transformer.fit_transform(CV.fit_transform(x_train))
    x_train_weight = tf_idf.toarray()
    tf_idf = transformer.transform(CV.transform(x_test))
    x_test_weight = tf_idf.toarray()
    print(x_test_weight)


    '''
    output:
    [[0.61335554 0.         0.         0.         0.78980693]]
    '''
