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


def __mention_to_db(dbcursor, db, mention, beg, context, src_doc_path, context_beg):
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

    mlen = mention.span[1] - mention.span[0] + 1
    try:
        dbcursor.execute("INSERT INTO mentions(beg, len, name_string, entity_type, context"
                         + ", src_doc_path, context_beg) VALUES (%d, %d, '%s', %d, '%s', '%s', %d)"
                         % (beg, mlen, mention.name, entity_type, context, src_doc_path, context_beg))
        db.commit()
    except:
        db.rollback()


def __process_file(dbcursor, db, med_link, sent_detector, filepath):
    mentions = med_link.mdel(filepath)

    fin = open(filepath, 'rb')
    doc_text = fin.read()
    doc_text = doc_text.replace('\r\n', '\n')
    doc_text = doc_text.decode('utf-8')
    fin.close()

    sent_spans = sent_detector.span_tokenize(doc_text)

    for m in mentions:
        print m.name, m.mtype, m.mesh_id, m.chebi_id, m.wid
        cb, ce = __get_context_span(m, sent_spans)
        mbeg = m.span[0] - cb
        context = doc_text[cb:ce]
        __mention_to_db(dbcursor, db, m, mbeg, context, filepath, cb)
        # break


def main():
    db = MySQLdb.connect('localhost', 'root', 'dhldhl', 'ksstudio')
    cursor = db.cursor()
    input_file = 'input/rsv1407.txt'
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    med_link = init_model()
    # __process_file(cursor, db, med_link, sent_detector, input_file)

    db.close()

if __name__ == '__main__':
    main()
