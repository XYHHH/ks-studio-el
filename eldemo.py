import os
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


def init_model():
    # extra_wiki_desc_file = 'e:/el/tmpres/demo/merge/wiki_extra_sentences.txt'
    # extra_parents_file = 'e:/el/tmpres/demo/extra_parents.txt'
    #
    # name_wid_file = 'e:/el/tmpres/demo/dict/single_candidates_wid_dict.txt'
    # record_file = 'd:/data/lab_demo/med_edl_data/records_info_with_wiki.txt'
    # dict_file = 'd:/data/lab_demo/med_edl_data/med_dict_ascii_with_ids_edited.txt'
    # tree_number_file = 'd:/data/lab_demo/med_edl_data/id_tn.txt'

    # res_dir = '/media/dhl/Data/el/tmpres/demo/del-data/'

    # input_file = '/media/dhl/Data/el/tmpres/NER/NER/00000001.txt.bak'
    # output_file = '/media/dhl/Data/el/tmpres/demo/result/result-linux.json'

    res_dir = 'e:/data/el/tmpres/demo/del-data/'
    extra_wiki_desc_file = res_dir + 'wiki_extra_sentences.txt'
    extra_parents_file = res_dir + 'extra_parents.txt'
    mesh_record_file = res_dir + 'records_info_with_wiki.txt'
    mesh_dict_file = res_dir + 'med_dict_ascii_with_ids_edited.txt'
    exclude_words_file = res_dir + 'exclude_words.txt'
    tree_number_file = res_dir + 'id_tn.txt'
    obo_file = res_dir + 'chebi.obo'

    word_idf_file = 'e:/data/el/tmpres/demo/word_idf.txt'

    # wiki_candidates_file = 'e:/el/tmpres/wiki/dict/name_candidates.txt'
    wiki_candidates_file = 'e:/data/el/tmpres/wiki/dict/name_candidates.pkl'

    # wiki_info_file = r'E:\el\tmpres\demo\wiki-med\new\wiki-info.txt'
    # links_file = r'E:\el\tmpres\demo\wiki-med\new\links.txt'
    # description_file = r'E:\el\tmpres\demo\wiki-med\new\text.txt'

    wiki_info_file = 'e:/data/el/tmpres/demo/wiki-all/wiki-info.pkl'
    links_file = 'e:/data/el/tmpres/demo/wiki-all/links.txt'
    description_file = 'e:/data/el/tmpres/demo/wiki-all/text.txt'

    mesh_extra_description_file = 'e:/data/el/tmpres/demo/extra_description_for_mesh.txt'

    chebi_terms = ChebiTerm.load_obo_file(obo_file)
    print '%d chebi terms' % len(chebi_terms)

    mesh_match = MeshMatch(mesh_dict_file, exclude_words_file)
    mesh_records = MeshRecord.load_mesh_records(mesh_record_file)
    mesh_tree = MeshTree(tree_number_file, mesh_records)

    wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    tfidf = TfIdf(word_idf_file)
    wiki_link = WikiLink(wiki_candidates_file, wiki_info, tfidf)
    extra_wiki_desc = ioutils.load_wiki_extra_descriptions(mesh_extra_description_file)
    # extra_wiki_desc = ioutils.load_wiki_extra_sentences(extra_wiki_desc_file)

    med_link = MedLink(extra_parents_file, mesh_match, mesh_records, mesh_tree, chebi_terms, wiki_info,
                       extra_wiki_desc, wiki_link)
    return med_link


def main():
    med_link = init_model()
    # input_file = 'input/00000001.txt'
    # output_file = 'output/result.json'
    # input_file = 'input/Disease.txt'
    # output_file = 'output/Disease-result.json'
    # input_file = 'input/newdisease.txt'
    # output_file = 'output/newdisease-result.json'
    input_file = 'input/rsv1407.txt'
    output_file = 'output/rsv1407-result.json'

    mdel_result = med_link.mdel(input_file)
    fout = open(output_file, 'wb')
    fout.write(mdel_result)
    fout.close()


def test():
    start_time = time()

    text = 'last opportunities Texas senator Cruz'

    word_idf_file = 'e:/el/tmpres/demo/merge/word_idf.txt'
    tfidf = TfIdf(word_idf_file)

    wiki_info_file = 'e:/el/tmpres/demo/wiki-all/wiki-info.pkl'
    links_file = 'e:/el/tmpres/demo/wiki-all/links.txt'
    description_file = 'e:/el/tmpres/demo/wiki-all/text.txt'
    wiki_info = WikiInfo(wiki_info_file, links_file, description_file)
    wiki_link = WikiLink('e:/el/tmpres/wiki/dict/name_candidates.pkl', wiki_info, tfidf)
    context_tfidf = tfidf.get_tfidf_from_text(text)
    print wiki_link.link_with_context('cruz', context_tfidf)

    print time() - start_time

    # while True:
    #     pass


if __name__ == '__main__':
    main()
    # test()
