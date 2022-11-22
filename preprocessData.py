# -*- coding:utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-


"""

加载json文件、去重
去除链接、标点、特殊符号
LTP分词
去除停用词
分词后长度小于2的文本都删除
保存新文档

"""
import re
import os
from ltp import StnSplit
import torch
from ltp import LTP
import json
# 保留的词性
from tqdm import tqdm
import emoji

POS_INCLUDED = ['n', 'ns', 'd', 'v', 'nh', 'a', 'nz', 'ni', 'i', 'j', 'ws', 'z', '%']
ltp = LTP(r"D:\本科资料存档\大四\NLP\论文代码\zhihu_analyize\model\base1")
# 将模型移动到 GPU 上
if torch.cuda.is_available():
    ltp.to("cuda")
ltp.add_words(
    ['开胸', '恶龙', '成隐', '吃瓜', '跨省', '罚酒', '主刀', '踢皮球', '重拳', '瞎搞', '开刀', '积液', '积水', '肺实变', '静脉曲张' '以药养医', '升职', '扩肛',
     '赚钱',
     '牢底坐穿', '拍片', '出事', '做事', '肝肾', '爆料', '前浪', '骚操作', '老鼠屎', '抽血', '做手术', '偏题', '守规矩', '杀猪', '赚钱', '悲壮', '倒逼', '见不得光',
     '自罚三杯', '饶命', '拉低', '见不得光', '人在做天在看', '哭爹喊娘', '贪钱'])
BATCH_SIZE = 32  # ltp推理batchsize，防止显存爆炸,我的电脑32比64快


class material_answer():

    def __init__(self, dict):
        self.url = 'url'
        self.username = 'username'
        self.userid = 'userid'
        self.like = 0
        self.type = 'self.type_indentify()'
        self.id = 'self.find_urlid()'
        self.text = 'find_replace(text)'
        self.comment = []
        self.__dict__.update(dict)
        self.text = self.proc(self.text)
        self.comment = [{
            'content': self.proc(i['content']),
            'like_num': i['like_num']
        }
            for i in self.comment]

    @classmethod
    def proc(self, text):
        text = re.sub(r'https://.*?/', '', text)  # 删除链接
        text = re.sub(r'/\w+', '', text)  # 删除链接纯数字字母
        text = re.sub(r'\[.*?]', '', text)  # 删除表情包
        text = re.sub(r'<.*?\"/>', '', text) #删除图片
        text = re.sub('<.*?>', '', text)  # 删除hmtl标签
        text = illegal_char(text)
        text = emoji.replace_emoji(text, replace="")
        text = re.sub(r'[​ \n\t]', '', text)
        text = text.replace(' ', '')
        text = text.replace('　', '')
        # 前端涉及特殊空格很多，此处的解决办法是遇到一个删一个，但也可以使用unicode编码进行正则匹配(上文illegal_char函数)，只筛选中英文和数字
        if text is None:
            return None
        outcws = []
        # outpos = []
        if len(text) > 500:
            text = sent_split(text)
            if len(text) > BATCH_SIZE:
                text = self.makebatch(self, text)
            else:
                text = [text]
            for b in text:
                cws, pos = splitWord(b)
                for nums, s in enumerate(cws):
                    for numw, word in enumerate(s):  # 遍历分词后的每一个单词
                        if word not in stopwords:  # 如果这个单词不在停用表里面
                            if pos[nums][numw] in POS_INCLUDED:
                                outcws.append(word)  # 就将这个词添加到结果中w
                                # outpos.append(pos[nums][numw])
        else:
            cws, pos = splitWord(text)
            for numw, word in enumerate(cws):  # 遍历分词后的每一个单词
                if word not in stopwords:  # 如果这个单词不在停用表里面
                    if pos[numw] in POS_INCLUDED:
                        outcws.append(word)  # 就将这个词添加到结果中w
                        # outpos.append(pos[nums][numw])
        return outcws

    @classmethod
    def delete_shortC(self, cls):
        nC = []
        for i in cls.comment:
            if len(i["content"]) >= 2:
                nC.append(i)
        cls.comment = nC

    def makebatch(self, list):
        batchlist = []
        numbatch = len(list) // BATCH_SIZE
        for p in range(numbatch):
            batchlist.append(list[BATCH_SIZE * p:BATCH_SIZE * p + BATCH_SIZE])
        batchlist.append(list[numbatch * BATCH_SIZE:len(list)])
        return batchlist


def illegal_char(s):
    s = re \
        .compile( \
        u"[^"
        u"\u4e00-\u9fa5"
        u"\u0041-\u005A"
        u"\u0061-\u007A"
        u"\u0030-\u0039"
        u"\u3002\uFF1F\uFF01\uFF0C\u3001\uFF1B\uFF1A\u300C\u300D\u300E\u300F\u2018\u2019\u201C\u201D\uFF08\uFF09\u3014\u3015\u3010\u3011\u2014\u2026\u2013\uFF0E\u300A\u300B\u3008\u3009"
        u"\!\@\#\$\%\^\&\*\(\)\-\=\[\]\{\}\\\|\;\'\:\"\,\.\/\<\>\?\/\*\+"
        u"]+") \
        .sub('', s)
    return s


def sent_split(text):
    sts = ['']
    allsentences = ['']
    sigments = re.findall('.{300}', text)
    for i in sigments:
        i = sts[-1] + i
        sts = StnSplit().split(i)
        allsentences.pop(-1)
        allsentences.extend(sts)
    allsentences = list(filter(None, allsentences))
    return allsentences


def splitWord(textlist):
    cws, pos = ltp.pipeline(textlist, tasks=["cws", "pos"]).to_tuple()  # to tuple 可以自动转换为元组格式
    # 使用元组格式作为返回结果
    return cws, pos


def stopwordslist_save():
    path = 'stopwords-master'
    flie_dir = os.listdir(path)
    stopwords = []
    for file in flie_dir:
        if not os.path.isdir(file):
            flie_name = os.path.join(path, file)
            print(flie_name)
            stopword = [line.strip() for line in open(flie_name, 'r', encoding='utf-8').readlines()]
            stopwords.extend(stopword)
        else:
            print('can not!!!')
    stopwords = list(set(stopwords))
    with open(r'stopwords-master\all_stopwords.txt', 'w', encoding='utf-8') as s:
        json.dump(stopwords, s, ensure_ascii=False)


def stopwordsList():
    with open(r'stopwords-master\all_stopwords.txt', encoding='utf-8') as l:
        return json.load(l)


stopwords = stopwordsList()


def deleteDu(a):  # article/answers
    newset = set()
    na = []
    for i in a:
        if i['url'] not in newset:
            newset.add(i['url'])
            na.append(i)
    # for i, c in enumerate(na[:]):  # 在这里na[:]相当于复制了一份，但是并不是同一份。
    #     if len(c['text']) < 2:
    #         na.pop(i)
    #         continue
    #     for j in c['comment']:
    #         if len(j['content']) < 5:
    #             c['comment'].remove(j)
    return na


if __name__ == '__main__':
    with open('allAnswers.json', encoding='utf-8') as j:
        j = json.load(j)
    j = deleteDu(j)
    al = open('SplitedAnswers.json', "a", encoding="utf-8")
    al.write('[')
    with tqdm(range(len(j)), desc='question') as tbar:
        for i in tbar:
            a = material_answer(j[i])
            # 删除过短文本
            # if len(a.text) < 2:
            #     continue
            # else:
            #     a.delete_shortC(a)
            json.dump(a.__dict__, al, ensure_ascii=False, indent=4)
            al.write(",\n")
            tbar.update()
    al.write(']')
    al.close()

    # a = [{
    #     "url": "https://www.zhihu.com/question/435980029/answer/262950351",
    #     "username": "匿名用户",
    #     "userid": NaN,
    #     "like": 45.0,
    #     "type": "answers",
    #     "id": "2629503518",
    #     "text": "<im  >  dsf \d esd \n",
    #     "comment": [
    #         {
    #             "content": "早就有人举报了，但是搞不倒他",
    #             "like_num": 20
    #         }
    #     ]
    # }, {
    #     "url": "https://www.zhihu.com/question/435980029/answer/2629503518",
    #     "username": "匿名用户",
    #     "userid": NaN,
    #     "like": 45.0,
    #     "type": "answers",
    #     "id": "2629503518",
    #     "text": "<img src=\"https://pica.zhimg.com/50/v2-816fd1561031e854711406253644d3d1_720w.jpg?source=1940ef5c\" data-rawwidth=\"1080\" data-rawheight=\"2400\" data-size=\"normal\" data-default-watermark-src=\"https://pic1.zhimg.com/50/v2-816fd1561031e854711406253644d3d1_720w.jpg?source=1940ef5c\" class=\"origin_image zh-lightbox-thumb\" width=\"1080\" data-original=\"https://pic1.zhimg.com/v2-816fd1561031e854711406253644d3d1_r.jpg?source=1940ef5c\"/>都火到了医考帮等各大平台。。。。。<img src=\"https://pic2.zhimg.com/50/v2-7d7cac04890abe51fc98265708865244_720w.jpg?source=1940ef5c\" data-rawwidth=\"1080\" data-rawheight=\"2400\" data-size=\"normal\" data-default-watermark-src=\"https://pic3.zhimg.com/50/v2-7d7cac04890abe51fc98265708865244_720w.jpg?source=1940ef5c\" class=\"origin_image zh-lightbox-thumb\" width=\"1080\" data-original=\"https://pic2.zhimg.com/v2-7d7cac04890abe51fc98265708865244_r.jpg?source=1940ef5c\"/>此人不倒，还身居部级医院的高位，对不起基层千千万万兢兢业业，忠于职守的医务工作者",
    #     "comment": [
    #         {
    #             "content": "早就有人举报了，但是搞不倒他",
    #             "like_num": 20
    #         }, {
    #             "content": "早就",
    #             "like_num": 0
    #         }, {
    #             "content": "早就有人举报了，但是搞不倒他",
    #             "like_num": 20
    #         }
    #     ]
    # }
    # ]
    # print(material_answer(a[0]).__dict__)
