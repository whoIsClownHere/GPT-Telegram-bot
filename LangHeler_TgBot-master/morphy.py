import csv
import pymorphy2


def morph(word):
    morh = pymorphy2.MorphAnalyzer()
    res = morh.parse(word)[0]
    haract = ','.join(str(res.tag).split(' ')).split(',')
    with open('data/pymorphy_tags.csv', encoding='Windows-1251') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        tags = dict(reader)
    message1 = "\n".join([tags[i] for i in haract])
    return message1
