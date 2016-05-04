# -*- coding: utf-8 -*-

from time import time
import os

from wikilink import WikiLink
from wikiinfo import WikiInfo
from preprocess.tfidf import TfIdf
import mentiondetection


def main():
    start_time = time()

    wiki_info_file = 'e:/el/tmpres/demo/wiki-all/wiki-info.pkl'
    links_file = 'e:/el/tmpres/demo/wiki-all/links.txt'
    description_file = 'e:/el/tmpres/demo/wiki-all/text.txt'
    wiki_candidates_file = 'e:/el/tmpres/wiki/dict/name_candidates.pkl'
    word_idf_file = 'e:/el/tmpres/demo/word_idf.txt'

    tfidf = TfIdf(word_idf_file)
    print tfidf.get_idf('acid')
    print tfidf.get_idf('football')

    wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    wiki_link = WikiLink(wiki_candidates_file, wiki_info, tfidf)

    input_file = 'input/00000001.txt'
    fin = open(input_file, 'rb')
    doc_text = fin.read()
    doc_text = doc_text.decode('utf-8')
    fin.close()

    pos = input_file.rfind('/')
    file_name = input_file[pos + 1:]
    ner_result_file = os.path.join('output', file_name + '.ner')
    merged_result_list = mentiondetection.clean_ner_result(ner_result_file)

    wiki_link.link_all(doc_text, merged_result_list)
    for mention in merged_result_list:
        if (not mention.mesh_id) and mention.chebi_id < 0 < mention.wid:
            cur_name = doc_text[mention.span[0]:mention.span[1] + 1].lower()
            print cur_name, mention.wid, wiki_info.get_info(mention.wid)[0]

    print time() - start_time
    # while True:
    #     pass


if __name__ == '__main__':
    main()
