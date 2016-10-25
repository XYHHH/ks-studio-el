# -*- coding: utf-8 -*-
import sys
import MySQLdb
import nltk.data
from eldemo import init_model


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


def test():
    name = u'戴dhl'
    age = 17
    db = MySQLdb.connect('localhost', 'root', 'dhldhl', 'dbtest', charset='utf8')
    cursor = db.cursor()
    # cursor.execute("SET NAMES utf8")
    # db.commit()
    try:
        cursor.execute(u"INSERT INTO students(name, age) VALUES (%s, %s)", (name, age))
        db.commit()
    except:
        print 'rolling back'
        e = sys.exc_info()[0]
        print e
        db.rollback()

    cursor.execute('SELECT * from students')
    print cursor.fetchall()
    db.close()


def main():
    # test()
    conn = MySQLdb.connect('localhost', 'root', 'dhldhl', 'ksstudio', charset='utf8')
    cursor = conn.cursor()
    input_file = 'input/rsv1407.txt'
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    med_link = init_model()
    __process_file(cursor, conn, med_link, sent_detector, input_file)
    conn.close()

if __name__ == '__main__':
    main()
