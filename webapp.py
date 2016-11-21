from flask import Flask, jsonify, abort, request
import json
import requests
from time import time
from meshtree import MeshTree
from meshrecord import MeshRecord
import ioutils
from medlink import MedLink
from chebiterm import ChebiTerm
from wikilink import WikiLink
from wikilinksimple import WikiLinkSimple
from wikiinfo import WikiInfo
from meshmatch import MeshMatch
from preprocess.tfidf import TfIdf
import mentiondetection
from mention import Mention
import os

app = Flask(__name__)


def init_model():
    res_dir = 'e:/data/el/tmpres/'
    del_res_dir = os.path.join(res_dir, 'demo/del-data/')
    # extra_wiki_desc_file = del_res_dir + 'wiki_extra_sentences.txt'
    # extra_parents_file = del_res_dir + 'extra_parents.txt'
    # mesh_record_file = del_res_dir + 'records_info_with_wiki.txt'
    # mesh_dict_file = del_res_dir + 'med_dict_ascii_with_ids_edited.txt'
    # exclude_words_file = del_res_dir + 'exclude_words.txt'
    # tree_number_file = del_res_dir + 'id_tn.txt'
    # obo_file = del_res_dir + 'chebi.obo'

    extra_wiki_desc_file = os.path.join(del_res_dir, 'wiki_extra_sentences.txt')
    extra_parents_file = os.path.join(del_res_dir, 'extra_parents.txt')
    mesh_record_file = os.path.join(del_res_dir, 'records_info_with_wiki.txt')
    mesh_dict_file = os.path.join(del_res_dir, 'med_dict_ascii_with_ids_edited.txt')
    exclude_words_file = os.path.join(del_res_dir, 'exclude_words.txt')
    tree_number_file = os.path.join(del_res_dir, 'id_tn.txt')
    obo_file = os.path.join(del_res_dir, 'chebi.obo')

    word_idf_file = os.path.join(res_dir, 'demo/word_idf.txt')
    wiki_candidates_file = os.path.join(res_dir, 'wiki/dict/name_candidates.pkl')
    wiki_info_file = os.path.join(res_dir, 'demo/wiki-all/wiki-info.pkl')
    links_file = os.path.join(res_dir, 'demo/wiki-all/links.txt')
    description_file = os.path.join(res_dir, 'demo/wiki-all/text.txt')
    mesh_extra_description_file = os.path.join(res_dir, 'demo/extra_description_for_mesh.txt')

    # wiki_candidates_file = 'e:/el/tmpres/wiki/dict/name_candidates.txt'
    # wiki_candidates_file = 'e:/data/el/tmpres/wiki/dict/name_candidates.pkl'
    # wiki_info_file = 'e:/data/el/tmpres/demo/wiki-all/wiki-info.pkl'
    # links_file = 'e:/data/el/tmpres/demo/wiki-all/links.txt'
    # description_file = 'e:/data/el/tmpres/demo/wiki-all/text.txt'
    # mesh_extra_description_file = 'e:/data/el/tmpres/demo/extra_description_for_mesh.txt'

    chebi_terms = ChebiTerm.load_obo_file(obo_file)

    mesh_match = MeshMatch(mesh_dict_file, exclude_words_file)
    mesh_records = MeshRecord.load_mesh_records(mesh_record_file)
    mesh_tree = MeshTree(tree_number_file, mesh_records)

    wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    tfidf = TfIdf(word_idf_file)
    wiki_link = WikiLink(wiki_candidates_file, wiki_info, tfidf)
    extra_wiki_desc = ioutils.load_wiki_extra_descriptions(mesh_extra_description_file)
    # extra_wiki_desc = ioutils.load_wiki_extra_sentences(extra_wiki_desc_file)

    tmp_med_link = MedLink(extra_parents_file, mesh_match, mesh_records, mesh_tree, chebi_terms, wiki_info,
                           extra_wiki_desc, wiki_link)
    return tmp_med_link


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


def mention_extraction_web(text):
    url = "http://10.214.129.188:8080/submit"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    print 'calling ', url
    data_json = json.dumps({"text": text})
    response = requests.request("POST", url, headers=headers, data=data_json)
    # print response.text
    print 'call end'
    return json.loads(response.text)


med_link = init_model()
# med_link = None


@app.route('/test/api/v1/addtask', methods=['POST'])
def create_task():
    ret_val = ''
    print request.headers
    print 'form:', request.form
    print 'args:', request.args
    print 'values:', request.values
    print 'stream:', request.stream
    print 'json:', request.json
    print 'data:', request.data
    if 'text' in request.values:
        ret_val = request.values['text']
        print ret_val
    return ret_val, 201


@app.route('/ks/api/v1/edl', methods=['POST'])
def edl_api():
    doc_text = ''
    if 'text' in request.values:
        doc_text = request.values['text']
        # print doc_text
        # print type(doc_text)
    else:
        abort(400)

    json_result = '[]'
    try:
        mentions_list = list()
        mentions_dict = mention_extraction_web(doc_text)
        for result_type, mentions in mentions_dict.items():
            entity_type = 'MISC'
            if result_type == 'results_Disease':
                entity_type = 'Disease'
            elif result_type == 'results_Chemical':
                entity_type = 'Chemical'

            for dict_mention in mentions:
                beg_pos = dict_mention['startChar']
                end_pos = dict_mention['endChar']
                meshid = None
                specified_type = dict_mention.get('label', None)
                if specified_type:
                    entity_type = specified_type
                # print dict_mention
                # print beg_pos, end_pos, entity_type, meshid
                m = Mention(span=(beg_pos, end_pos), mtype=entity_type, mesh_id=meshid)
                mentions_list.append(m)
        # linked_mentions = med_link.link_mentions(mentions_list, doc_text.decode('utf-8'))
        linked_mentions = med_link.link_mentions(mentions_list, doc_text)
        json_result = json.dumps(__mentions_to_dict_list(linked_mentions))
    except:
        print 'except'
    print json_result + '\n'
    return json_result
    # return 'OK'


if __name__ == '__main__':
    # med_link = init_model()
    app.run(debug=True)
