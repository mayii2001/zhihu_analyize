import json


def savejson(path, dic):
    """

    :param path:
    :param dic:
    :return:
    """
    with open(path, "w", encoding="utf-8") as j:
        json.dump(dic,j, ensure_ascii=False, indent=4)


def loadjson(path):
    with open(path, "r", encoding="utf-8") as j:
        json.load(j)


