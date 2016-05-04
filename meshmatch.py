from time import time
from collections import deque
from itertools import izip


class TrieNode:
    def __init__(self, s=None, rid=None):
        self.s = s
        self.rid = rid
        self.childlist = None

    def add_val(self, s, rid):
        common_len = TrieNode.__len_common_prefix(self.s, s)
        if common_len == len(s):
            if common_len < len(self.s):
                new_node = TrieNode(self.s[common_len:])
                new_node.childlist = self.childlist
                new_node.rid = self.rid
                self.rid = rid
                self.childlist = [new_node]
                self.s = self.s[:common_len]
            else:
                self.rid = rid
            return

        sleft = s[common_len:]

        if common_len == len(self.s):
            if not self.childlist:
                self.childlist = [TrieNode(sleft, rid)]
                return
            for child in self.childlist:
                if child.s[0] == sleft[0]:
                    # print sleft, rid, common_len, s, self.s, 'he'
                    child.add_val(sleft, rid)
                    return
            self.childlist.append(TrieNode(sleft, rid))
            return

        new_node = TrieNode(self.s[common_len:])
        new_node.childlist = self.childlist
        new_node.rid = self.rid
        self.rid = None
        self.childlist = [new_node]
        self.s = self.s[:common_len]
        self.childlist.append(TrieNode(sleft, rid))

    def find_val(self, s):
        if not self.childlist:
            return None
        for child in self.childlist:
            if child.s == s:
                return child.rid
            if s.startswith(child.s):
                return child.find_val(s[len(child.s):])
        return None

    def match_text(self, text, pos, match_list):
        if self.rid:
            match_list.append((self.rid, pos - 1))
        if pos >= len(text):
            return
        if not self.childlist:
            return
        for child in self.childlist:
            if text[pos:].startswith(child.s):
                child.match_text(text, pos + len(child.s), match_list)

    def print_tree(self):
        node_queue = deque([self])

        while len(node_queue):
            cur_node = node_queue.popleft()
            print 'id: %d, s: %s' % (id(cur_node), cur_node.s),
            if cur_node.rid:
                print cur_node.rid,
            print ''
            if cur_node.childlist:
                for child in cur_node.childlist:
                    node_queue.append(child)
                    print id(child)

    @staticmethod
    def __len_common_prefix(s0, s1):
        common_pos = 0
        for ch0, ch1 in izip(s0, s1):
            if ch0 != ch1:
                break
            common_pos += 1
        return common_pos


class MeshMatch:
    word_sep = [',', '.', '"', '\'', '(', ')', '/', '-', '\n', ';']

    def __init__(self, dict_file, exclude_words_file):
        exclude_words_set = None
        if exclude_words_file:
            exclude_words_set = MeshMatch.__load_exclude_words(exclude_words_file)

        self.trie_root = TrieNode('')

        print 'Loading mesh dict ...'
        fin = open(dict_file, 'rb')
        fin.readline()
        cur_name = None
        line_idx = 0
        for line_idx, line in enumerate(fin):
            line = line.strip()
            if cur_name:
                cur_rid = line

                if cur_name.isupper():
                    self.trie_root.add_val(cur_name, cur_rid)
                    cur_name = None
                    continue

                cur_name_lc = cur_name.lower()
                if not exclude_words_set or cur_name_lc not in exclude_words_set:
                    self.trie_root.add_val(cur_name, cur_rid)
                    # self.add_term(cur_name, cur_rid)
                    if cur_name_lc != cur_name:
                        self.trie_root.add_val(cur_name_lc, cur_rid)
                        # self.add_term(cur_name_lc, cur_rid)

                cur_name = None
            else:
                cur_name = line.decode('utf-8')
        fin.close()

    def match(self, text, beg_pos):
        match_list = list()
        self.trie_root.match_text(text, beg_pos, match_list)

        if not match_list:
            return None

        max_pos = -1
        rid = None
        for match_tup in match_list:
            if match_tup[1] > max_pos:
                max_pos = match_tup[1]
                rid = match_tup[0]
        return (beg_pos, max_pos), rid

    def find_all_terms(self, doc_text):
        span_list = list()
        id_list = list()
        # results = list()
        pos = 0
        text_len = len(doc_text)
        while pos < text_len:
            # print doc_text[pos:]
            result = self.match(doc_text, pos)
            if result and (result[0][1] == text_len - 1 or MeshMatch.__is_word_sep(doc_text[result[0][1] + 1])):
                # results.append(result)
                span_list.append(result[0])
                id_list.append(result[1])
                pos = result[0][1] + 1
            else:
                while pos < text_len and not MeshMatch.__is_word_sep(doc_text[pos]):
                    pos += 1
                pos += 1
        return span_list, id_list

    @staticmethod
    def __is_word_sep(ch):
        if ch.isspace():
            return True
        return ch in MeshMatch.word_sep

    @staticmethod
    def __load_exclude_words(file_name):
        fin = open(file_name, 'rb')
        fin.next()
        words_set = set()
        for line in fin:
            words_set.add(line.strip())
        fin.close()
        return words_set


def main():
    start_time = time()
    dict_file = 'd:/data/lab_demo/med_edl_data/med_dict_ascii_with_ids_edited.txt'
    mesh_match = MeshMatch(dict_file, None)
    text = 'Human Immunodeficiency Virus (HIV) Antigen-Antibody'
    span_list, id_list = mesh_match.find_all_terms(text)
    for span, rid in izip(span_list, id_list):
        print text[span[0]:span[1] + 1], rid
    # mesh_match.match('RNA Bacteriophages', 0)
    # print mesh_detector.match('RNA', 0)
    print time() - start_time


if __name__ == '__main__':
    main()
