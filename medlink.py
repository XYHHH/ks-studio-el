from itertools import izip
import json
import os
import re

from mention import Mention
import mentiondetection

mesh_types_dict = {'A': 'Anatomy', 'B': 'Organism', 'C': 'Disease', 'D': 'Chemical', 'F': 'Psychology'}


class MedLink:
    def __init__(self, extra_parents_file, mesh_match, mesh_records, mesh_tree, chebi_terms, wiki_info,
                 extra_wiki_descriptions, wiki_link):
        self.wiki_link = wiki_link
        self.mesh_records = mesh_records
        self.chebi_terms = chebi_terms
        self.wiki_info = wiki_info
        self.mesh_match = mesh_match
        self.mesh_tree = mesh_tree
        self.extra_wiki_descriptions = extra_wiki_descriptions
        self.__load_extra_parents(extra_parents_file)

    def mdel(self, file_path):
        # mention detection
        pos = file_path.rfind('/')
        file_name = file_path[pos + 1:]
        ner_result_file = os.path.join('output', file_name + '.ner')

        # read text
        fin = open(file_path, 'rb')
        doc_text = fin.read()
        doc_text = doc_text.replace('\r\n', '\n')
        doc_text = doc_text.decode('utf-8')
        fin.close()

        merged_result_list = mentiondetection.clean_ner_result(ner_result_file)
        return self.link_text(doc_text, merged_result_list)

    def link_text(self, text, mention_detection_result):
        result_dict = dict()

        mesh_mention_list = self.__find_mesh_mentions(text)
        merged_mention_list = list()
        Mention.merge_mention_list(mention_detection_result, merged_mention_list)
        Mention.merge_mention_list(mesh_mention_list, merged_mention_list)

        merged_mention_list.sort(key=lambda x: x.span[0])

        for mention in merged_mention_list:
            mention.name = text[mention.span[0]:mention.span[1] + 1]

        if self.wiki_link.tfidf:
            self.wiki_link.link_all(text, merged_mention_list)
        else:
            self.__link_mention_to_wiki(text, merged_mention_list)

        for mention in merged_mention_list:
            if mention.mesh_id or mention.chebi_id > -1:
                for mention1 in merged_mention_list:
                    if mention.name.lower() == mention1.name.lower():
                        mention1.mesh_id = mention.mesh_id
                        mention1.chebi_id = mention.chebi_id

        mesh_idx_dict, wiki_idx_dict, chebi_idx_dict, idx_list = MedLink.__asign_indices(merged_mention_list)
        # print wiki_idx_dict

        result_dict['entities'] = entities_dict = dict()
        self.__add_wiki_mention_info(wiki_idx_dict, entities_dict)
        self.__add_mesh_mention_info(mesh_idx_dict, entities_dict)
        self.__add_chebi_mention_info(chebi_idx_dict, entities_dict)

        result_span_list = list()
        mention_type_list = list()
        for mention in merged_mention_list:
            result_span_list.append(mention.span)
            mention_type_list.append(mention.mtype)

        self.__fix_types(mesh_idx_dict, idx_list, mention_type_list)

        result_dict['spans'] = result_span_list
        result_dict['idx'] = idx_list
        result_dict['type'] = mention_type_list

        return json.dumps(result_dict, indent=2)

    def __fix_types(self, mesh_idx_dict, idx_list, type_list):
        idx_type_dict = dict()
        for mesh_id, idx in mesh_idx_dict.iteritems():
            cur_record = self.mesh_records.get(mesh_id, None)
            if not cur_record:
                continue
            if cur_record.mns:
                cur_type = mesh_types_dict.get(cur_record.mns[0][0], None)
                if cur_type:
                    idx_type_dict[idx] = cur_type
        for i, idx, in enumerate(idx_list):
            cur_type = idx_type_dict.get(idx, None)
            if cur_type:
                type_list[i] = cur_type

    def __link_wiki(self, text, mention_span):
        cur_name = text[mention_span[0]:mention_span[1] + 1].lower()
        return self.wiki_link.link(cur_name)

    def __wiki_info_to_dict(self, wid, rec_dict, mesh_id=None):
        rec_dict['wid'] = wid

        # wiki_info = self.wiki_info_dict.get(wid, None)
        title, description, links = self.wiki_info.get_info(wid)
        if not title:
            return

        result_links = list()
        for link in links:
            if '#' in link or ':' in link or '[[' in link:
                continue
            result_links.append(link)

        # rec_dict['wiki-title'] = wiki_info[0]
        # rec_dict['wiki-links'] = wiki_info[1]
        rec_dict['wiki-title'] = title
        rec_dict['wiki-links'] = result_links

        if mesh_id:
            extra_wiki_desc = self.extra_wiki_descriptions.get(mesh_id, None)
            if extra_wiki_desc:
                rec_dict['wiki-text'] = extra_wiki_desc
        else:
            # rec_dict['wiki-text'] = wiki_info[2]
            description = description.replace(' ( )', '')
            description = re.sub('\[\[(.*?)\]\]', '\g<1>', description)
            rec_dict['wiki-text'] = description

    def __add_wiki_mention_info(self, wiki_idx_dict, entity_info_dict):
        for wid, idx in wiki_idx_dict.iteritems():
            entity_info_dict[idx] = cur_rec_dict = dict()
            self.__wiki_info_to_dict(wid, cur_rec_dict)

            extra_parents = self.wiki_extra_parents.get(wid, None)
            if extra_parents:
                cur_rec_dict['extra-parent'] = self.__gen_tree_path_lists(extra_parents)

    def __add_mesh_mention_info(self, mesh_idx_dict, entity_info_dict):
        for mesh_id, idx in mesh_idx_dict.iteritems():
            entity_info_dict[idx] = cur_rec_dict = dict()

            cur_record = self.mesh_records.get(mesh_id, None)
            if not cur_record:
                continue

            cur_rec_dict['mesh-id'] = mesh_id
            cur_rec_dict['mesh-name'] = cur_record.name
            cur_rec_dict['mesh-synonyms'] = cur_record.terms
            cur_rec_dict['mesh-description'] = cur_record.mesh_desc
            cur_rec_dict['mesh-tn'] = cur_record.mns
            if cur_record.mns:
                parents_info_dict = dict()
                for mn in cur_record.mns:
                    parents_info_dict[mn] = self.__gen_tree_path_list(mn)
                cur_rec_dict['mesh-parents'] = parents_info_dict

            extra_parents = self.mesh_extra_parents.get(mesh_id, None)
            if extra_parents:
                cur_rec_dict['extra-parent'] = self.__gen_tree_path_lists(extra_parents)

            if cur_record.wid > -1:
                self.__wiki_info_to_dict(cur_record.wid, cur_rec_dict, mesh_id)

    def __add_chebi_mention_info(self, chebi_idx_dict, entity_info_dict):
        for chebi_id, idx in chebi_idx_dict.iteritems():
            entity_info_dict[idx] = cur_rec_dict = dict()
            cur_rec_dict['chebi-id'] = chebi_id
            chebi_term = self.chebi_terms.get(chebi_id, None)
            if not chebi_term:
                print chebi_id + ' not found.'
                continue

            cur_rec_dict['chebi-name'] = chebi_term.name
            cur_rec_dict['chebi-description'] = chebi_term.description
            cur_rec_dict['chebi-synonyms'] = chebi_term.synonyms
            cur_rec_dict['chebi-isa'] = chebi_term.isa

            wid = self.wiki_link.link(chebi_term.name.lower())
            if wid > -1:
                self.__wiki_info_to_dict(wid, cur_rec_dict)

    def __gen_tree_path_list(self, tree_number):
        parents_list = self.mesh_tree.get_parents(tree_number)
        parents_info_list = list()
        for mesh_parent in parents_list:
            parents_info_list.append((mesh_parent[0], self.mesh_records[mesh_parent[0]].name,
                                      mesh_parent[1]))
        return parents_info_list

    def __gen_tree_path_lists(self, parents_record_ids):
        tree_paths = list()
        for parent_id in parents_record_ids:
            parent_record = self.mesh_records[parent_id]
            tree_paths.append(self.__gen_tree_path_list(parent_record.mns[0]))
        return tree_paths

    def __load_extra_parents(self, extra_parents_file):
        print 'loading', extra_parents_file
        self.mesh_extra_parents = dict()
        self.wiki_extra_parents = dict()

        fin = open(extra_parents_file, 'rb')
        for line in fin:
            vals = line.strip().split('\t')

            parent_list = list()
            if vals[1] == 'null':
                self.wiki_extra_parents[int(vals[0])] = parent_list
            else:
                self.mesh_extra_parents[vals[1]] = parent_list

            num_lines = int(vals[3])
            for i in xrange(num_lines):
                pvals = fin.next().strip().split('\t')
                parent_list.append(pvals[0])
        fin.close()

    def __find_mesh_mentions(self, text):
        mesh_spans, mesh_ids = self.mesh_match.find_all_terms(text)
        mention_list = list()
        for mesh_span, mesh_id in izip(mesh_spans, mesh_ids):
            mention = Mention()
            mention.span = mesh_span
            mention.mtype = 'MISC'
            mention.mesh_id = mesh_id
            mention_list.append(mention)
        return mention_list

    @staticmethod
    def __asign_indices(mention_list):
        mesh_idx_dict = dict()
        wiki_idx_dict = dict()
        chebi_idx_dict = dict()
        idx_list = list()
        idx_cnt = 0
        for mention in mention_list:
            cur_idx = -1
            if mention.mesh_id:
                cur_idx = mesh_idx_dict.get(mention.mesh_id, -1)
                if cur_idx == -1:
                    cur_idx = mesh_idx_dict[mention.mesh_id] = idx_cnt
                    idx_cnt += 1
            elif mention.chebi_id > -1:
                cur_idx = chebi_idx_dict.get(mention.chebi_id, -1)
                if cur_idx == -1:
                    cur_idx = chebi_idx_dict[mention.chebi_id] = idx_cnt
                    idx_cnt += 1
            elif mention.wid > -1:
                cur_idx = wiki_idx_dict.get(mention.wid, -1)
                if cur_idx == -1:
                    cur_idx = wiki_idx_dict[mention.wid] = idx_cnt
                    # print cur_idx, mention.wid
                    idx_cnt += 1
            idx_list.append(cur_idx)
        return mesh_idx_dict, wiki_idx_dict, chebi_idx_dict, idx_list

    def __link_mention_to_wiki(self, text, mention_list):
        for mention in mention_list:
            # if not mention.mesh_id and not mention.chebi_id:
            if not mention.mesh_id and mention.chebi_id < 0:
                link_wid = self.__link_wiki(text, mention.span)
                mention.wid = link_wid
                # print text[mention.span[0]:mention.span[1] + 1], mention.wid
