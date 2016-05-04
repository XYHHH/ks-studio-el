from mention import Mention


def span_exist(cur_span, span_list):
    for sp in span_list:
        if not ((cur_span[1] < sp[0]) or cur_span[0] > sp[1]):
            return True
    return False


def clean_ner_result(result_file):
    ord_mention_list = list()
    med_mention_list = list()

    fin = open(result_file, 'rb')
    for line in fin:
        line = line.strip()
        if len(line) == 0:
            continue

        vals = line.strip().split('\t')
        # TODO
        if vals[3] == 'Disease' or vals[3] == 'Chemical':
            span = (int(vals[0]), int(vals[1]) - 1)
        else:
            span = (int(vals[0]), int(vals[1]))
        mention = Mention()
        mention.span = span
        mention.mtype = vals[3]
        if len(vals) == 4:
            ord_mention_list.append(mention)
        else:
            if vals[4].startswith('MESH'):
                mention.mesh_id = vals[4][5:]
            elif vals[4].startswith('CHEBI'):
                mention.chebi_id = int(vals[4][6:])
            med_mention_list.append(mention)
    fin.close()

    merged_mention_list = list()
    Mention.merge_mention_list(med_mention_list, merged_mention_list)
    Mention.merge_mention_list(ord_mention_list, merged_mention_list)

    return merged_mention_list
