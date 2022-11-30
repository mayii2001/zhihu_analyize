# coding:utf-8

import json
import utils
import pandas as pd

with open("data/SplitedAnswers_Comments_Q.json", encoding='utf-8') as ac:
    ac = json.load(ac)

with open("data/SplitedzhuanlanComments2.json", encoding='utf-8') as zc:
    zc = json.load(zc)


def takeGroup(group):
    z = pd.read_csv('data/zhuanlans_reserved.csv')
    z = z[z['group'] == group]
    a = pd.read_excel('data/Question_reserved.xlsx')
    a = a[a['group'] == group]
    detail_Of_Group = pd.concat([a, z], ignore_index=True)
    return detail_Of_Group[['url', 'title']]


if __name__ == '__main__':
    for i in [1, 2, 3, 4]:
        OneGroup = takeGroup(i)
        doc = []
        try:
            for a in ac:
                if a['url'][0:40] in OneGroup['url'].tolist():
                    a['title'] = OneGroup['title'][OneGroup['url'] == a['url'][0:40]].tolist()[0]
                    # 因为dataframe保留索引所以先tolist()
                    doc.append(a)
            for a in zc:
                if a['url'] in OneGroup['url']:
                    a['title'] = OneGroup['title'][OneGroup['url'] == a['url'][0:40]].tolist()[0]
                    doc.append(a)
            utils.savejson(f'data/grouped/{i}.json', doc)
        except KeyError:
            print(OneGroup['title'][OneGroup['url'] == a['url'][0:40]])
