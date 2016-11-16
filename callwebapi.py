# -*- coding: utf-8 -*-
import requests
import urllib
from eldemo import init_model
from mention import Mention

from nltk.tag import StanfordNERTagger


def call_ner():
    url = "http://10.214.129.188:8080/submit"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
        # 'postman-token': "ddd0f7f2-d85f-d3b2-b619-e4a597c32db8"
    }

    response = requests.request("POST", url, headers=headers, data='{"text": "HIV."}')

    # print(response.text)
    print response.text


def call_edl():
    url_get_base = "http://localhost:5000/ks/api/v1/edl"
    args = {
        'text': 'Barack Obama is an American politician.'
    }
    result = urllib.urlopen(url_get_base, urllib.urlencode(args))  # POST method
    content = result.read().strip()
    print content


def __mentions_to_dict_list(mentions):
    mentions_dict_list = list()
    for m in mentions:
        d = dict()
        d['span'] = m.span
        d['type'] = m.mtype
        if m.wid:
            d['wiki_id'] = m.wid
        if m.mesh_id:
            d['mesh_id'] = m.mesh_id
        if m.chebi_id > -1:
            d['chebi_id'] = m.chebi_id
        mentions_dict_list.append(d)
    return mentions_dict_list


def link():
    print 'beg init'
    med_link = init_model()
    curtext = 'Obama is an American politician.'
    m = Mention(span=(0, 4), mtype='PER')
    mentions = [m]
    lr = med_link.link_mentions(mentions, curtext)
    print __mentions_to_dict_list(lr)


def main():
    # call_ner()
    call_edl()
    # link()

    # st = StanfordNERTagger('e:/lib/stanford-nlp/stanford-ner-2015-12-09/classifiers'
    #                        '/english.all.3class.distsim.crf.ser.gz')
    # st.tag('Rami Eid is studying at Stony Brook University in NY'.split())
    # data_to_pass = u'text="Michael Jordan the machine learning scientist. 戴"'.encode('utf-8')
    # r = requests.post('http://localhost:5000/ks/api/v1/edl', data=data_to_pass)
    # data_to_pass = 'cool, man'
    # r = requests.post('http://localhost:5000/test/api/v1/addtask', data=data_to_pass)
    # print r.text

if __name__ == '__main__':
    main()
