# -*- coding: utf-8 -*-
import sys
# import MySQLdb
import mentiondetection
import nltk.data
from eldemo import init_model
from wikilink import WikiLink
from wikiinfo import WikiInfo
from meshmatch import MeshMatch
from preprocess.tfidf import TfIdf
from medlink import MedLink


def __get_context_span(mention, sent_spans):
    span_idx_beg, span_idx_end = -1, -1
    for i in xrange(len(sent_spans)):
        if mention.span[0] >= sent_spans[i][0]:
            span_idx_beg = i
        if span_idx_end == -1 and mention.span[1] < sent_spans[i][1]:
            span_idx_end = i
        if span_idx_end > -1:
            break

    if span_idx_beg > 0:
        span_idx_beg -= 1
    if span_idx_end < len(sent_spans) - 1:
        span_idx_end += 1

    return sent_spans[span_idx_beg][0], sent_spans[span_idx_end][1]


def __mention_to_db(dbcursor, dbconn, mention, beg, context, src_doc_path, context_beg):
    entity_type = 0
    if mention.mtype == 'PER':
        entity_type = 1
    elif mention.mtype == 'ORG':
        entity_type = 2
    elif mention.mtype == 'LOC':
        entity_type = 3
    elif mention.mtype == 'Chemical':
        entity_type = 4
    elif mention.mtype == 'Disease':
        entity_type = 5

    candidates_str = ''
    if mention.candidates:
        candidates_str = ';'.join([str(wid) for wid in mention.candidates])

    # it's possible for a mention to be linked to multiple KB's
    # give ID's of different KB's different leading characters
    entity_id = ''
    if mention.mesh_id:
        entity_id += 'M%s' % mention.mesh_id
    if mention.chebi_id > -1:
        if entity_id:
            entity_id += ';'
        entity_id += 'C%d' % mention.chebi_id
    if mention.wid > -1:
        if entity_id:
            entity_id += ';'
        entity_id += 'W%d' % mention.wid

    mlen = mention.span[1] - mention.span[0] + 1
    try:
        dbcursor.execute(u"INSERT INTO mentions(beg, len, name_string, entity_type, context"
                         + u", src_doc_path, context_beg) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                         (beg, mlen, mention.name, entity_type, context, src_doc_path, context_beg))
        dbcursor.execute(u"INSERT INTO entity_linking(mention_id, candidates, entity_id) VALUES (LAST_INSERT_ID(),"
                         + u" %s, %s)", (candidates_str, entity_id))
        dbconn.commit()
    except:
        print 'rolling back'
        print (beg, mlen, mention.name, entity_type, context, src_doc_path, context_beg)
        dbconn.rollback()


def __mentions_to_db(mentions, doc_text, sent_spans, dbcursor, dbconn, filepath):
    for m in mentions:
        # print m.name, m.mtype, m.mesh_id, m.chebi_id, m.wid
        cb, ce = __get_context_span(m, sent_spans)
        mbeg = m.span[0] - cb
        context = doc_text[cb:ce]
        __mention_to_db(dbcursor, dbconn, m, mbeg, context, filepath, cb)


def __process_file(dbcursor, dbconn, med_link, sent_detector, filepath):
    mentions = med_link.mdel(filepath)

    fin = open(filepath, 'rb')
    doc_text = fin.read()
    doc_text = doc_text.replace('\r\n', '\n')
    doc_text = doc_text.decode('utf-8')
    fin.close()

    sent_spans = sent_detector.span_tokenize(doc_text)
    __mentions_to_db(mentions, doc_text, sent_spans, dbcursor, dbconn, filepath)


def __test():
    word_idf_file = 'e:/data/el/tmpres/demo/word_idf.txt'
    wiki_candidates_file = 'e:/data/el/tmpres/wiki/dict/name_candidates.pkl'
    wiki_info_file = 'e:/data/el/tmpres/demo/wiki-all/wiki-info.pkl'
    links_file = 'e:/data/el/tmpres/demo/wiki-all/links.txt'
    description_file = 'e:/data/el/tmpres/demo/wiki-all/text.txt'

    input_file = 'input/rsv1407.txt'
    ner_result_file = 'output/rsv1407.txt.ner'
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    fin = open(input_file, 'rb')
    doc_text = fin.read()
    doc_text = doc_text.replace('\r\n', '\n')
    doc_text = doc_text.decode('utf-8')
    fin.close()

    mentions = mentiondetection.clean_ner_result(ner_result_file)

    # wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    # tfidf = TfIdf(word_idf_file)
    # wiki_link = WikiLink(wiki_candidates_file, wiki_info, tfidf)
    # med_link = MedLink(wiki_info=wiki_info, wiki_link=wiki_link)

    # mentions = med_link.mdel(input_file)

    # med_link.link_mentions(mentions, doc_text)

    for m in mentions:
        print '%d\t%d\t%s\t%s\t%d\t%d' % (m.span[0], m.span[1], m.name, m.mesh_id, m.chebi_id, m.wid)


def main():
    conn = MySQLdb.connect('localhost', 'root', 'dhldhl', 'ksstudio', charset='utf8')
    cursor = conn.cursor()
    input_file = 'input/rsv1407.txt'
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    med_link = init_model()
    __process_file(cursor, conn, med_link, sent_detector, input_file)
    conn.close()

if __name__ == '__main__':
    # main()
    __test()
