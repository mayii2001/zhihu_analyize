# coding:utf-8
"""

加载json文件、去重
去除链接、标点、特殊符号
LTP分词
去除停用词
保存新文档

"""
import re
import requests
import json
import os
import pandas as pd
import logging

from numpy import NaN


class material():
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)


if __name__ == '__main__':
    a = [{
            "url": "https://www.zhihu.com/question/435980029/answer/2629503518",
            "username": "匿名用户",
            "userid": NaN,
            "like": 45.0,
            "type": "answers",
            "id": "2629503518",
            "text": "<im",
            "comment": [
                {
                    "content": "早就有人举报了，但是搞不倒他",
                    "like_num": 20
                }
            ]
        },{
        "url": "https://www.zhihu.com/question/435980029/answer/2629503518",
        "username": "匿名用户",
        "userid": NaN,
        "like": 45.0,
        "type": "answers",
        "id": "2629503518",
        "text": "<img src=\"https://pica.zhimg.com/50/v2-816fd1561031e854711406253644d3d1_720w.jpg?source=1940ef5c\" data-rawwidth=\"1080\" data-rawheight=\"2400\" data-size=\"normal\" data-default-watermark-src=\"https://pic1.zhimg.com/50/v2-816fd1561031e854711406253644d3d1_720w.jpg?source=1940ef5c\" class=\"origin_image zh-lightbox-thumb\" width=\"1080\" data-original=\"https://pic1.zhimg.com/v2-816fd1561031e854711406253644d3d1_r.jpg?source=1940ef5c\"/>都火到了医考帮等各大平台。。。。。<img src=\"https://pic2.zhimg.com/50/v2-7d7cac04890abe51fc98265708865244_720w.jpg?source=1940ef5c\" data-rawwidth=\"1080\" data-rawheight=\"2400\" data-size=\"normal\" data-default-watermark-src=\"https://pic3.zhimg.com/50/v2-7d7cac04890abe51fc98265708865244_720w.jpg?source=1940ef5c\" class=\"origin_image zh-lightbox-thumb\" width=\"1080\" data-original=\"https://pic2.zhimg.com/v2-7d7cac04890abe51fc98265708865244_r.jpg?source=1940ef5c\"/>此人不倒，还身居部级医院的高位，对不起基层千千万万兢兢业业，忠于职守的医务工作者",
        "comment": [
            {
                "content": "早就有人举报了，但是搞不倒他",
                "like_num": 20
            }
        ]
    }
    ]
    for i,c in enumerate(a):
        if len(c['text'])<5:
            a.pop(i)
            continue
    print(a)
