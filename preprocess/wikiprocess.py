import re
from itertools import izip
import cPickle as pickle
from array import array
from time import time

from meshrecord import MeshRecord
from meshtree import MeshTree
from preprocess.tfidf import TfIdf
from textprocess import tokenized_text_match, find_sentence_ends
from wikiinfo import WikiInfo
from nltk import word_tokenize, sent_tokenize


def __parent_exist(cur_mesh_record, new_parent_id, mesh_tree):
    for id_mn in cur_mesh_record.mns:
        if id_mn == new_parent_id:
            return True
        parents = mesh_tree.get_parents(id_mn)
        for tup in parents:
            if tup[0] == new_parent_id:
                return True


def __load_isa(isa_file):
    fin = open(isa_file, 'rb')
    wid_isa_dict = dict()
    for line in fin:
        vals = line.strip().split('\t')
        wid = int(vals[0])
        cur_name = vals[1]
        num_lines = int(vals[2])
        rids = list()
        for i in xrange(num_lines):
            vals = fin.next().strip().split('\t')
            if vals[1] != 'null':
                rids.append(vals[1])

        if rids:
            wid_isa_dict[wid] = (cur_name, rids)
    fin.close()
    return wid_isa_dict


def add_matches_to_list(text, miter, match_list):
    for m in miter:
        text_part = text[m.span()[0]:m.span()[1]]
        match_list.append(text_part)


# TODO consider redirect
def get_wiki_title_mesh_dict(mesh_records_file):
    title_mesh_dict = dict()
    records = MeshRecord.load_mesh_records(mesh_records_file)
    for mesh_id, record in records.iteritems():
        if record.wiki_title:
            title_mesh_dict[record.wiki_title.lower()] = mesh_id
    return title_mesh_dict


def get_original_sentences(text, words_to_pos_list, sentence_ends):
    sentences = list()
    cur_beg_word_idx = 0
    for end_word_idx in sentence_ends:
        sentences.append(text[words_to_pos_list[cur_beg_word_idx]:words_to_pos_list[end_word_idx] + 1])
        cur_beg_word_idx = end_word_idx + 1
    return sentences


def get_tfidf_of_sentences(text_words, sentences_ends, tfidf):
    tfidf_vecs = list()
    beg_idx = 0
    for idx in sentences_ends:
        cur_sentence_words = text_words[beg_idx:idx + 1]
        tfidf_vecs.append(tfidf.get_tfidf(cur_sentence_words))
        beg_idx = idx + 1
    return tfidf_vecs


def __get_sentences_to_add(prev_text_words, prev_sentence_ends, new_text_words, new_sentence_ends, tfidf):
    prev_tfidf_vecs = get_tfidf_of_sentences(prev_text_words, prev_sentence_ends, tfidf)
    new_tfidf_vecs = get_tfidf_of_sentences(new_text_words, new_sentence_ends, tfidf)
    wanted_sentence_indices = list()
    for nidx, new_tfidf_vec in enumerate(new_tfidf_vecs):
        to_add = True
        for pidx, prev_tfidf_vec in enumerate(prev_tfidf_vecs):
            sim_val = TfIdf.sim(new_tfidf_vec, prev_tfidf_vec)
            if sim_val > 0.95:
                to_add = False
                # print sim_val, 'too similar'
                break
        if to_add:
            wanted_sentence_indices.append(nidx)
    return wanted_sentence_indices


def gen_extra_sentences():
    word_idf_file = 'e:/el/tmpres/demo/merge/word_idf.txt'
    tfidf = TfIdf(word_idf_file)

    mesh_id_wid_file = 'e:/el/tmpres/demo/merge/mesh_id_wid.txt'
    merged_desc_file = 'e:/el/tmpres/demo/merge/merged_descriptions.txt'
    merged_tokenized_desc_file = 'e:/el/tmpres/demo/merge/merged_descriptions_tokenized.txt'
    extra_sentence_file = 'e:/el/tmpres/demo/merge/wiki_extra_sentences.txt'

    mesh_ids = list()
    wids = list()
    fin = open(mesh_id_wid_file, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        mesh_ids.append(vals[0])
        wids.append(int(vals[1]))
    fin.close()

    fin_desc = open(merged_desc_file, 'rb')
    fin_token_desc = open(merged_tokenized_desc_file, 'rb')
    fout = open(extra_sentence_file, 'wb')
    for idx, (mesh_id, mesh_desc, mesh_token_desc) in enumerate(izip(mesh_ids, fin_desc, fin_token_desc)):
        mesh_token_desc = mesh_token_desc.strip()
        mesh_desc_words = mesh_token_desc.split(' ')
        mesh_sentence_ends = find_sentence_ends(mesh_desc_words)

        wiki_desc = fin_desc.next().strip()
        wiki_token_desc = fin_token_desc.next().strip()
        wiki_desc_words = wiki_token_desc.split(' ')
        wiki_sentence_ends = find_sentence_ends(wiki_desc_words)

        extra_sentence_indices = __get_sentences_to_add(mesh_desc_words, mesh_sentence_ends,
                                                        wiki_desc_words, wiki_sentence_ends, tfidf)

        wiki_words_to_pos_list = tokenized_text_match(wiki_desc, wiki_desc_words)
        original_sentences = get_original_sentences(wiki_desc, wiki_words_to_pos_list, wiki_sentence_ends)
        fout.write('%s\t%d\n' % (mesh_id, len(extra_sentence_indices)))
        for j in extra_sentence_indices:
            fout.write('%s\n' % original_sentences[j])

        # if idx == 10000:
        #     break
    fin_desc.close()
    fin_token_desc.close()
    fout.close()


def merge_descriptions():
    mesh_records_file = 'd:/data/lab_demo/med_edl_data/record_infos_with_wiki.txt'
    wiki_wid_file = 'e:/el/tmpres/demo/wiki-med/wid.txt'
    wiki_pos_file = 'e:/el/tmpres/demo/wiki-med/pos.txt'
    wiki_text_file = 'e:/el/tmpres/demo/wiki-med/text.txt'

    mesh_id_wid_file = 'e:/el/tmpres/demo/mesh_id_wid.txt'
    merged_desc_file = 'e:/el/tmpres/demo/merged_descriptions.txt'

    fin_wid = open(wiki_wid_file, 'rb')
    fin_pos = open(wiki_pos_file, 'rb')
    fin_text = open(wiki_text_file, 'rb')
    wiki_text_dict = dict()
    for idx, (wid_line, pos_line) in enumerate(izip(fin_wid, fin_pos)):
        wid = int(wid_line.strip())
        vals = pos_line.strip().split('\t')
        num_lines = int(vals[1])
        text = ''
        for i in xrange(num_lines):
            cur_text_line = fin_text.readline()
            if i == 0:
                text += cur_text_line
        wiki_text_dict[wid] = text
    fin_wid.close()
    fin_pos.close()
    fin_text.close()

    print wiki_text_dict[5668]

    # fout0 = open(mesh_id_wid_file, 'wb')
    # fout1 = open(merged_desc_file, 'wb')
    # mesh_records = MeshRecord.load_mesh_records(mesh_records_file)
    # for mesh_id, record in mesh_records.iteritems():
    #     wiki_text = wiki_text_dict.get(record.wid, '')
    #     if wiki_text and record.mesh_desc:
    #         fout0.write('%s\t%d\n' % (mesh_id, record.wid))
    #         fout1.write('%s\n' % record.mesh_desc)
    #         # fout.write(record.mesh_desc)
    #         fout1.write(wiki_text)
    # fout0.close()
    # fout1.close()


def find_is_a():
    mesh_records_file = 'd:/data/lab_demo/med_edl_data/record_infos_with_wiki.txt'
    title_mesh_dict = get_wiki_title_mesh_dict(mesh_records_file)

    wid_file = 'e:/el/tmpres/demo/wiki-med/wid.txt'
    title_file = 'e:/el/tmpres/demo/wiki-med/title.txt'
    pos_file = 'e:/el/tmpres/demo/wiki-med/pos.txt'
    wiki_text_file = 'e:/el/tmpres/demo/wiki-med/text-with-links.txt'
    dst_is_a_file = 'e:/el/tmpres/demo/wiki-med/is_a.txt'

    fin_wid = open(wid_file, 'rb')
    fin_title = open(title_file, 'rb')
    fin_pos = open(pos_file, 'rb')
    fin_text = open(wiki_text_file, 'rb')
    fout = open(dst_is_a_file, 'wb')
    for wid_line, title_line, pos_line in izip(fin_wid, fin_title, fin_pos):
        cur_wid = int(wid_line.strip())
        cur_title = title_line.strip()

        cur_text = ''
        vals = pos_line.strip().split('\t')
        num_lines = int(vals[3])
        for i in xrange(num_lines):
            cur_text += fin_text.readline()

        matches = list()
        cur_text_lower = cur_text.lower()
        pattern_str = '\[\[(.*?)\|(.*?)\]\]'
        miter = re.finditer(pattern_str, cur_text_lower)
        match_str0 = cur_title.lower() + ' is a '
        match_str1 = cur_title.lower() + ' is an '
        for m in miter:
            mesh_id = title_mesh_dict.get(m.group(1).lower(), 'null')
            prev_text = cur_text_lower[:m.start()]
            if prev_text.endswith(match_str0):
                matches.append(('%s is a %s' % (cur_title, cur_text[m.start():m.end()]), mesh_id))
            elif prev_text.endswith(match_str1):
                matches.append(('%s is an %s' % (cur_title, cur_text[m.start():m.end()]), mesh_id))

        if len(matches) > 0:
            fout.write('%d\t%s\t%d\n' % (cur_wid, cur_title, len(matches)))
            for match in matches:
                fout.write('%s\t%s\n' % (match[0], match[1]))

    fin_wid.close()
    fin_title.close()
    fin_pos.close()
    fin_text.close()
    fout.close()


def gen_extra_parent_with_isa():
    mesh_record_file = 'd:/data/lab_demo/med_edl_data/records_info_with_wiki.txt'
    tree_number_file = 'd:/data/lab_demo/med_edl_data/id_tn.txt'
    isa_file = 'e:/el/tmpres/demo/wiki-med/is_a.txt'

    dst_extra_parent_file = 'e:/el/tmpres/demo/extra_parents.txt'

    mesh_records = MeshRecord.load_mesh_records(mesh_record_file)
    mesh_tree = MeshTree(tree_number_file, mesh_records)

    wid_mesh_id_dict = dict()
    for mesh_id, rec in mesh_records.iteritems():
        if rec.wid:
            wid_mesh_id_dict[rec.wid] = mesh_id

    wid_isa_dict = __load_isa(isa_file)
    fout = open(dst_extra_parent_file, 'wb')
    for wid, isa_tup in wid_isa_dict.iteritems():
        cur_mesh_id = wid_mesh_id_dict.get(wid, '')
        if cur_mesh_id:
            cur_mesh_record = mesh_records[cur_mesh_id]
            extra_parent_list = list()
            for isa_mesh_id in isa_tup[1]:
                if not __parent_exist(cur_mesh_record, isa_mesh_id, mesh_tree):
                    parent_mesh_rec = mesh_records[isa_mesh_id]
                    extra_parent_list.append((isa_mesh_id, parent_mesh_rec.name))

            if len(extra_parent_list) > 0:
                fout.write('%d\t%s\t%s\t%d\n' % (wid, cur_mesh_id, cur_mesh_record.name, len(extra_parent_list)))
                for tup in extra_parent_list:
                    fout.write('%s\t%s\n' % (tup[0], tup[1]))
        else:
            fout.write('%d\tnull\t%s\t%d\n' % (wid, isa_tup[0], len(isa_tup[1])))
            for mesh_id in isa_tup[1]:
                fout.write('%s\t%s\n' % (mesh_id, mesh_records[mesh_id].name))
    fout.close()


def gen_links():
    wiki_text_pos_file = 'e:/el/tmpres/demo/wiki-med/pos.txt'
    text_with_links_file = 'e:/el/tmpres/demo/wiki-med/text-with-links.txt'
    dst_links_file = 'e:/el/tmpres/demo/wiki-med/links.txt'

    fin_pos = open(wiki_text_pos_file, 'rb')
    fin_text = open(text_with_links_file, 'rb')
    fout = open(dst_links_file, 'wb')
    for line in fin_pos:
        vals = line.strip().split('\t')
        num_lines = int(vals[3])
        for i in xrange(num_lines):
            text_line = fin_text.next().strip()
            if i == 0:
                miter = re.finditer(r'\[\[(.*?)\|(.*?)\]\]', text_line)
                for midx, m in enumerate(miter):
                    if midx > 0:
                        fout.write('\t')
                    fout.write(m.group(1))
        fout.write('\n')
    fin_pos.close()
    fin_text.close()
    fout.close()


def wiki_info_to_pkl():
    wiki_info_file = r'E:\el\tmpres\demo\wiki-all\wiki-info.txt'
    dst_pkl_file = 'e:/el/tmpres/demo/wiki-all/wiki-info.pkl'
    start_time = time()
    wids, titles, text_positions = list(), list(), list()
    fin_info = open(wiki_info_file, 'rb')
    for line in fin_info:
        wid = int(line.strip())
        title = fin_info.next().strip()
        pos_vals = fin_info.next().strip().split('\t')

        wids.append(wid)
        titles.append(title)
        text_positions.append(int(pos_vals[0]))
    fin_info.close()
    print titles[:10]
    print time() - start_time
    while True:
        pass

    # wids = array('l', wids)
    # text_positions = array('l', text_positions)
    # info_dict = {'wids': wids, 'text_pos': text_positions, 'titles': titles}
    # fout = open(dst_pkl_file, 'wb')
    # pickle.dump(info_dict, fout, 2)
    # fout.close()


def __sentences_to_tfidf_vecs(sentences, tfidf):
    tfidf_list = list()
    for sent in sentences:
        words = word_tokenize(sent)
        tfidf_vec = tfidf.get_tfidf(words)
        tfidf_list.append(tfidf_vec)
    return tfidf_list


def __get_extra_wiki_description(mesh_text, wiki_text, tfidf):
    mesh_sents = sent_tokenize(mesh_text)
    wiki_sents = sent_tokenize(wiki_text)
    mesh_tfidf_list = __sentences_to_tfidf_vecs(mesh_sents, tfidf)
    wiki_tfidf_list = __sentences_to_tfidf_vecs(wiki_sents, tfidf)

    extra_description = ''
    for i, wiki_tfidf_vec in enumerate(wiki_tfidf_list):
        have_similar = False
        for j, mesh_tfidf_vec in enumerate(mesh_tfidf_list):
            sim_val = tfidf.sim(wiki_tfidf_vec, mesh_tfidf_vec)
            if sim_val > 0.95:
                # print sim_val, 'SIMILAR:'
                # print mesh_sents[j]
                # print wiki_sents[i]
                have_similar = True
                break
        if not have_similar:
            extra_description += ' ' + wiki_sents[i]

    if len(extra_description) > 1:
        extra_description = extra_description[1:]
        if extra_description[-1].isalpha():
            extra_description += '.'
        elif extra_description[-1] == ':':
            extra_description = extra_description[:-1] + '.'
        return extra_description
    return ''


def gen_extra_description_for_mesh():
    res_dir = 'e:/el/tmpres/demo/del-data/'
    mesh_record_file = res_dir + 'records_info_with_wiki.txt'
    wiki_info_file = 'e:/el/tmpres/demo/wiki-all/wiki-info.pkl'
    description_file = 'e:/el/tmpres/demo/wiki-all/text.txt'
    links_file = 'e:/el/tmpres/demo/wiki-all/links.txt'
    word_idf_file = 'e:/el/tmpres/demo/word_idf.txt'

    dst_file = 'e:/el/tmpres/demo/extra_description_for_mesh.txt'

    tfidf = TfIdf(word_idf_file)
    wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    mesh_records = MeshRecord.load_mesh_records(mesh_record_file)

    # wiki_text = wiki_info.get_info(37220)[1]
    # __get_extra_wiki_description('', wiki_text, tfidf)
    fout = open(dst_file, 'wb')
    for i, (mesh_id, record) in enumerate(mesh_records.iteritems()):
        if record.wid < 0:
            continue
        info = wiki_info.get_info(record.wid)
        if info and info[1]:
            mesh_text = record.mesh_desc.decode('utf-8')
            wiki_text = info[1].decode('utf-8')
            extra_desc = __get_extra_wiki_description(mesh_text, wiki_text, tfidf)
            fout.write('%s\n%s\n' % (mesh_id, extra_desc.encode('utf-8')))
        # if i > 10:
        #     break
    fout.close()


def test():
    start_time = time()
    dst_pkl_file = 'e:/el/tmpres/demo/wiki-all/wiki-info.pkl'
    fin = open(dst_pkl_file, 'rb')
    wiki_info_dict = pickle.load(fin)
    fin.close()
    print wiki_info_dict['wids'][:10]
    print wiki_info_dict['titles'][:10]
    print time() - start_time
    while True:
        pass


def main():
    # find_is_a()
    # merge_descriptions()
    # gen_extra_sentences()
    # gen_extra_parent_with_isa()
    # gen_links()
    # wiki_info_to_pkl()
    gen_extra_description_for_mesh()

if __name__ == '__main__':
    main()
    # test()
