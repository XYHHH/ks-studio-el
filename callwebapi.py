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
    url_get_base = "http://10.214.129.104:5000/ks/api/v1/edl"
    args = {
        'text': 'Barack Obama is an American politician.'
        # 'text': 'In 2009, Elliot Turner launched AlchemyAPI to process the written word, '
        #         'with all of its quirks and nuances, and got immediate traction. That first month, '
        #         'the company\'s eponymous language-analysis API processed 500,000 transactions. Today '
        #         'it\'s processing three billion transactions a month, or about 1,200 a second. “That\'s '
        #         'a growth rate of 6,000 times over three years,” touts Turner. “Context is '
        #         'super-important,” he adds. “\'I\'m dying\' is a lot different than \'I\'m dying to buy'
        #         ' the new iPhone.\'” “As we move into new markets, we\'re going to be making some new '
        #         'hires," Turner says. "We knocked down some walls and added 2,000 square feet to our '
        #         'office.” “We\'re providing the ability to translate human language in the form of '
        #         'web pages and documents into actionable data,” Turner says. Clients include Walmart, '
        #         'PR Newswire and numerous publishers and advertising networks. “This allows a news '
        #         'organization to detect what a person likes to read about,” says Turner of '
        #         'publishers and advertisers.'
        # 'text': 'it is good'
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
    curtext = '“That\'s a growth rate of 6,000 times over three years,” touts Turner.'
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
