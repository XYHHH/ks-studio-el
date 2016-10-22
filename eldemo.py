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
    res_dir = '/media/dhl/Data/data/edl/demo'
    # res_dir = 'e:/el/tmpres/demo/del-data/'

    # extra_wiki_desc_file = res_dir + 'wiki_extra_sentences.txt'
    extra_parents_file = os.path.join(res_dir, 'del-data/extra_parents.txt')
    mesh_record_file = os.path.join(res_dir, 'del-data/records_info_with_wiki.txt')
    mesh_dict_file = os.path.join(res_dir, 'del-data/med_dict_ascii_with_ids_edited.txt')
    exclude_words_file = os.path.join(res_dir, 'del-data/exclude_words.txt')
    tree_number_file = os.path.join(res_dir, 'del-data/id_tn.txt')
    obo_file = os.path.join(res_dir, 'del-data/chebi.obo')

    word_idf_file = os.path.join(res_dir, 'word_idf.txt')

    wiki_candidates_file = os.path.join(res_dir, 'wiki/name_candidates.pkl')

    wiki_info_file = os.path.join(res_dir, 'wiki/wiki-info.pkl')
    links_file = os.path.join(res_dir, 'wiki/links.txt')
    description_file = os.path.join(res_dir, 'wiki/text.txt')

    mesh_extra_description_file = os.path.join(res_dir, 'extra_description_for_mesh.txt')

    chebi_terms = ChebiTerm.load_obo_file(obo_file)

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

    mdel_result = med_link.mdel_tojson(input_file)
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
