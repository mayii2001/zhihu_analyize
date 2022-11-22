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
from PIL import Image
from io import BytesIO
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
    pics = re.findall('<img src="(https://pic.*?\.zhimg\.com.*?)\"', txt)
    return pics


def getpic(url):
    picpool = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    }
    request = requests.Session()
    request.headers.clear()
    if len(url) == 0:
        print("No picture at all!")
        return 0
    for i in url:
        if 'gif' in i:
            picpool.append(None)
            continue
        res = request.get(url=i, headers=headers)
        if res.status_code != 200:
            print("Connect Fail!")
            picpool.append(None)
            continue
        elif res.content is None:
            print("No picture get!")
            picpool.append(None)
            continue
        elif 'webp' in i:
            picpool.append(change_webp_to_jpg(res.content))
        else:
            picpool.append(res.content)
    print(f"{len(picpool)} Pictures collect over!")
    return picpool


def change_webp_to_jpg(webp_content):
    """
    将webp图片格式转换为jpg格式
    :param webp_content: webp图片字节流
    :return: jpg图片字节流
    from: https://blog.csdn.net/weixin_43411585/article/details/107787613
    """
    jpg_content = ""
    try:
        if webp_content.upper().startswith(b"RIF"):
            im = Image.open(BytesIO(webp_content))
            if im.mode == "RGBA":
                im.load()
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[3])
                im = background
            img_byte = BytesIO()
            im.save(img_byte, format='JPEG')
            jpg_content = img_byte.getvalue()
    except Exception as err:
        logging.error(err)
    return jpg_content if jpg_content else webp_content


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
            # 此处是cpu版本，gpu使用text.append(res[1][0])
    return text


def find_replace(str):
    urls = findpic_url(str)
    pics = getpic(urls)
    over = str
    if pics == 0:
        return str
    for i in range(len(urls)):
        if pics[i] is not None:
            stroP = ''.join(paddleocr(pics[i]))
            url = '<img src=\"' + re.escape(urls[i]) + '.*?>'
            over = re.sub(url,stroP, over)
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
    test = '这种败类，真是震碎了我的三观！刷新了我能接受的本就不怎么高的底线……这样无疑为本来就紧张的医患关系更是火上浇油了。各自安好，洗洗睡吧。<img src="https://picx1.zhimg.com/50/v2-fcd289756f72aab923fc315d1c5509ed_720w.jpg?source=1940ef5c" data-rawwidth=""868"" data-rawheight=""1856"" data-size=""normal"" data-default-watermark-src=""https://pica.zhimg.com/50/v2-02b46b1ba83ae9d52d89d0539a0d1693_720w.jpg?source=1940ef5c"" class=""origin_image zh-lightbox-thumb"" width=""868"" data-original=""https://picx1.zhimg.com/v2-fcd289756f72aab923fc315d1c5509ed_r.jpg?source=1940ef5c""/><img src=""https://picx1.zhimg.com/50/v2-cbaa4d75003ef81ef105be3cad9da4bb_720w.jpg?source=1940ef5c"" data-rawwidth=""858"" data-rawheight=""1681"" data-size=""normal"" data-default-watermark-src=""https://pic1.zhimg.com/50/v2-9f37e7e0b76c144c8b8da822e41fa586_720w.jpg?source=1940ef5c"" class=""origin_image zh-lightbox-thumb"" width=""858"" data-original=""https://picx1.zhimg.com/v2-cbaa4d75003ef81ef105be3cad9da4bb_r.jpg?source=1940ef5c""/><img src=""https://pic1.zhimg.com/50/v2-35a05bed4e9516ee597df3c9f253c1c4_720w.jpg?source=1940ef5c"" data-rawwidth=""846"" data-rawheight=""1440"" data-size=""normal"" data-default-watermark-src=""https://picx1.zhimg.com/50/v2-f5b5773b80906a1840961cda2c3cca20_720w.jpg?source=1940ef5c"" class=""origin_image zh-lightbox-thumb"" width=""846"" data-original=""https://pic1.zhimg.com/v2-35a05bed4e9516ee597df3c9f253c1c4_r.jpg?source=1940ef5c""/>'
    print(find_replace(test))
if __name__ == '__mai':
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
    with tqdm(range(2, len(oa)), desc='question') as tbar:
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
