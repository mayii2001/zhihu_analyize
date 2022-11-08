# coding:utf-8
"""

使用八爪鱼爬取专栏、问答的url、点赞、内容
调用paddleocr对内容ocr（后续上云平台运行程序）
调用api获取对应的评论内容和评论点赞
保存为json格式（后续需要手动删除最后的逗号和加列表符号）

"""
import re
import requests
import json
from paddleocr import PaddleOCR
import os
import pandas as pd
from tqdm import tqdm
import logging

logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def savedocument(articles, type):
    with open("all{}.json".format(type), 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


class article:

    def __init__(self, url, text, title, like):
        self.url = url
        self.title = title
        self.like = float(like)
        self.type = self.type_indentify()
        self.id = self.find_urlid()
        self.text = find_replace(text)
        self.comment = self.getcomment(self.type, self.id)

    def __str__(self):
        return str(self.__dict__)

    def find_urlid(self):
        if self.type == "answers":
            return re.findall(r"\d+\.?\d*", self.url)[1]
        else:
            return re.findall(r"\d+\.?\d*", self.url)[0]

    def type_indentify(self):
        if re.search("question", self.url) is not None:
            return "answers"
        elif re.search("zhuanlan", self.url) is not None:
            return "articles"

    def getcomment(self, type, id):
        all_com = []
        url = 'https://www.zhihu.com/api/v4/comment_v5/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
        }

        url = url + type + '/' + id + '/root_comment?order_by=like_count'
        while True:
            request = requests.Session()
            request.headers.clear()
            res = request.get(url=url, headers=headers)
            if res.status_code != 200:
                print("Connect Failed!")
                exit()
            else:
                print("start collecting!")

            js = json.loads(res.text)

            for i in js['data']:
                all_com.append({
                    "content": i['content'],
                    "like_num": i['like_count'],
                })

            if len(js['data']) == 20:
                url = js['paging']['next']
                print("next page started")
            else:
                print("FINISH!")
                return all_com


def findpic_url(txt):
    pics = re.findall('https://pic.\.zhimg\.com.*?\"', txt)
    return pics


def getpic(url):
    picpool = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    }
    request = requests.Session()
    request.headers.clear()
    if len(url) == 0:
        print("no picture!")
        return 0
    for i in url:
        if 'gif' in i:
            picpool.append(None)
            continue
        res = request.get(url=i[0:-1], headers=headers)
        if res.status_code != 200:
            print("Connect Fail!")
            picpool.append(None)
            continue
        elif res.content is None:
            print("No picture!")
            picpool.append(None)
            continue
        else:
            picpool.append(res.content)
    print("Pictures collect over!")
    return picpool


def paddleocr(img):
    """
    img：二进制格式输入
    返回一个列表
    """
    ocr = PaddleOCR(use_gpu=True, use_angle_cls=True, det=False, lang="ch", parallel_nn=True)

    results = ocr.ocr(img, cls=True)
    text = []
    for idx in range(len(results)):
        res = results[idx]
        for line in res:
            text.append(line[1][0])
    return text


def find_replace(str):
    urls = findpic_url(str)
    pics = getpic(urls)
    over = str
    if pics == 0:
        return str
    for i in range(len(urls)):
        if pics[i] is not None:
            stroP = '。'.join(paddleocr(pics[i]))
            url = re.compile('<img src="' + urls[i] + '.*?>')
            over = re.sub(url, " " + stroP + "。 ", over)
    return over


class Answers(article):
    def __init__(self, url, username, userid, text, like):
        self.url = url
        self.username = username
        self.userid = userid
        self.like = float(like)
        self.type = self.type_indentify()
        self.id = self.find_urlid()
        self.text = find_replace(text)
        self.comment = self.getcomment(self.type, self.id)


def getlike(x):
    x = re.search("\d+\.?\d*", str(x))
    if x is not None:
        return x.group()
    else:
        return 0


if __name__ == '__main__':
    # allZ=pd.read_csv('知乎专栏2.csv',skip_blank_lines=False)
    # al = open('allzhuanlan.json', "a", encoding="utf-8")
    # with tqdm(range(81,len(allZ)), desc='zhuanlan') as tbar:
    #     for i in tbar:
    #         a = article(allZ["url"][i],allZ["text"][i],allZ["标题"][i],allZ["like"][i])
    #         json.dump(a.__dict__,al,ensure_ascii=False, indent=4)
    #         al.write(",\n")
    #         tbar.update()
    # al.close()
    #
    oa = pd.read_csv('allQuestions.csv')
    # oa.drop_duplicates(subset='url', keep='first', inplace=True)
    # oa.dropna(axis=0, subset=["richtext"],inplace=True)
    # oa.dropna(axis=0, subset=["url"], inplace=True) #index会乱
    # oa.reset_index(drop=True,inplace=True)
    # oa['button3'] = oa["button3"].apply(lambda x: getlike(x))
    # print(oa['richtext'][85])
    al = open('allAnswers.json', "a", encoding="utf-8")
    with tqdm(range(len(oa)), desc='question') as tbar:
        for i in tbar:
            a = Answers(oa["url"][i], oa['用户'][i], oa['用户_链接'][i], oa["richtext"][i], oa["button3"][i])
            json.dump(a.__dict__, al, ensure_ascii=False, indent=4)
            al.write(",\n")
            tbar.update()
    al.close()

    # d1=pd.read_csv('otherall2.csv')
    # d2=pd.read_csv('answerlist_435980029.csv')
    # d=pd.concat([d1,d2])
    # d.drop_duplicates(subset='url', keep='first', inplace=True)
    # d.dropna(axis=0, subset=["richtext"],inplace=True)
    # d.dropna(axis=0, subset=["url"], inplace=True) #index会乱
    # d.reset_index(drop=True,inplace=True)
    # d['button3'] = d["button3"].apply(lambda x: getlike(x))
    # d.to_csv('allQuestions.csv',encoding='utf-8')
