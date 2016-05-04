from meshrecord import MeshRecord
from itertools import izip
import re


def __load_extra_sentences_for_mesh(file_name):
    print 'loading', file_name
    extra_desc = dict()
    fin = open(file_name, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        num_lines = int(vals[1])
        sentences = ''
        for i in xrange(num_lines):
            if i != 0:
                sentences += ' '
            sentences += fin.next().strip()
        sentences = re.sub(r'<ref .*?</ref>', '', sentences)
        if not sentences.endswith('may refer to:'):
            extra_desc[vals[0]] = sentences
    fin.close()

    return extra_desc


def __load_extra_description_for_mesh(file_name):
    print 'loading', file_name
    extra_desc = dict()
    fin = open(file_name, 'rb')
    for line in fin:
        description = fin.next().strip()
        description = re.sub(r'<ref .*?</ref>', '', description)
        if not description.endswith('may refer to:'):
            extra_desc[line.strip()] = description
    fin.close()
    return extra_desc


def load_wiki_extra_descriptions(file_name, multi_sentences=False):
    if multi_sentences:
        return __load_extra_sentences_for_mesh(file_name)
    else:
        return __load_extra_description_for_mesh(file_name)


# def load_wiki_info(wiki_info_file, links_file, desc_file=None):
#     wiki_info_dict = dict()
#
#     fin_info = open(wiki_info_file)
#     fin_links = open(links_file, 'rb')
#
#     fin_desc = None
#     if desc_file:
#         fin_desc = open(desc_file, 'rb')
#
#     for info_line, links_line in izip(fin_info, fin_links):
#         wid = int(wid_line.strip())
#         cur_title = title_line.strip()
#         cur_anchors = anchor_text_line.strip().split('\t')
#
#         cur_desc = ''
#         if fin_desc_pos:
#             pos_line = fin_desc_pos.readline()
#             pos_vals = pos_line.strip().split('\t')
#             cur_desc_num_lines = int(pos_vals[1])
#             for i in xrange(cur_desc_num_lines):
#                 cur_text_line = fin_desc.readline()
#                 if i == 0:
#                     cur_desc += cur_text_line.strip()
#
#         wiki_info_dict[wid] = (cur_title, cur_anchors, cur_desc)
#
#     fin_wid.close()
#     fin_title.close()
#     fin_anchor_text.close()
#
#     if fin_desc_pos:
#         fin_desc_pos.close()
#     if fin_desc:
#         fin_desc.close()
#
#     return wiki_info_dict


def load_wiki_info(wid_file, title_file, anchor_text_file, desc_pos_file=None, desc_file=None):
    wiki_info_dict = dict()

    fin_wid = open(wid_file, 'rb')
    fin_title = open(title_file, 'rb')
    fin_anchor_text = open(anchor_text_file, 'rb')

    fin_desc_pos = fin_desc = None
    if desc_pos_file:
        fin_desc_pos = open(desc_pos_file, 'rb')
        fin_desc = open(desc_file, 'rb')

    for wid_line, title_line, anchor_text_line in izip(
            fin_wid, fin_title, fin_anchor_text):
        wid = int(wid_line.strip())
        cur_title = title_line.strip()
        cur_anchors = anchor_text_line.strip().split('\t')

        cur_desc = ''
        if fin_desc_pos:
            pos_line = fin_desc_pos.readline()
            pos_vals = pos_line.strip().split('\t')
            cur_desc_num_lines = int(pos_vals[1])
            for i in xrange(cur_desc_num_lines):
                cur_text_line = fin_desc.readline()
                if i == 0:
                    cur_desc += cur_text_line.strip()

        wiki_info_dict[wid] = (cur_title, cur_anchors, cur_desc)

    fin_wid.close()
    fin_title.close()
    fin_anchor_text.close()

    if fin_desc_pos:
        fin_desc_pos.close()
    if fin_desc:
        fin_desc.close()

    return wiki_info_dict


def load_int_list_file_to_list(file_name):
    val_list = list()
    f = open(file_name)
    for tmpline in f:
        val_list.append(int(tmpline.strip()))
    f.close()
    return val_list


def load_int_list_file_to_set(file_name):
    val_set = set()
    f = open(file_name)
    for tmpline in f:
        val_set.add(int(tmpline.strip()))
    f.close()
    return val_set


def load_name_wid_file(name_wid_file):
    name_wid_dict = dict()
    fin = open(name_wid_file, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        name_wid_dict[vals[0]] = vals[1]
    fin.close()

    return name_wid_dict


def load_mesh_records(record_file):
    records = dict()
    fin = open(record_file, 'rb')
    num_records = int(fin.readline().strip())
    for i in xrange(num_records):
        rec = MeshRecord()
        rec.name = fin.readline().strip()
        rec.rid = fin.readline().strip()
        wid = fin.readline().strip()
        rec.wid = None if wid == 'null' else wid
        rec.wiki_title = fin.readline().strip()
        rec.mesh_desc = fin.readline().strip()

        rec.terms = list()
        num_terms = fin.readline().strip()
        # num_terms = int(fin.readline().strip())
        num_terms = int(num_terms)
        for j in xrange(num_terms):
            rec.terms.append(fin.readline().strip())

        rec.mns = list()
        num_mns = int(fin.readline().strip())
        for j in xrange(num_mns):
            rec.mns.append(fin.readline().strip())

        records[rec.rid] = rec

    fin.close()

    return records
