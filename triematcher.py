class TrieNode:
    def __init__(self):
        self.ch = None
        self.child = None
        self.next_child = None
        self.rid = None

    def add_child(self, ch):
        if not self.child:
            self.child = TrieNode()
            self.child.ch = ch
            return self.child

        cur_child = self.child
        while cur_child.ch != ch and cur_child.next_child:
            cur_child = cur_child.next_child
        if cur_child.ch == ch:
            return cur_child

        cur_child.next_child = TrieNode()
        cur_child.next_child.ch = ch
        return cur_child.next_child

    def find_child(self, ch):
        cur_child = self.child
        while cur_child:
            if cur_child.ch == ch:
                return cur_child
            cur_child = cur_child.next_child
        return None


class MeshDetect:
    word_sep = [',', '.', '"', '\'', '(', ')', '/', '-', '\n', ';']

    def __init__(self, dict_file, exclude_words_file):
        exclude_words_set = None
        if exclude_words_file:
            exclude_words_set = MeshDetect.load_exclude_words(exclude_words_file)

        self.trie_root = TrieNode()

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
                    self.add_term(cur_name, cur_rid)
                    cur_name = None
                    continue

                cur_name_lc = cur_name.lower()
                if not exclude_words_set or cur_name_lc not in exclude_words_set:
                    self.add_term(cur_name, cur_rid)
                    if cur_name_lc != cur_name:
                        self.add_term(cur_name_lc, cur_rid)

                cur_name = None
            else:
                cur_name = line.decode('utf-8')
        fin.close()

        print line_idx, 'lines'

    def add_term(self, term, rid):
        cur_node = self.trie_root
        for ch in term:
            cur_node = cur_node.add_child(ch)
        if not cur_node.rid:
            cur_node.rid = rid

    def match(self, text, beg_pos):
        cur_node = self.trie_root
        pos = beg_pos
        hit_node = None
        hit_pos = -1
        result_span = [beg_pos, -1]
        while pos < len(text) and cur_node:
            cur_node = cur_node.find_child(text[pos])
            if cur_node and cur_node.rid:
                hit_node = cur_node
                hit_pos = pos
            pos += 1

        if hit_node:
            result_span[1] = hit_pos
            return result_span, hit_node.rid

        return None

    def find_all_terms(self, doc_text):
        span_list = list()
        id_list = list()
        # results = list()
        pos = 0
        text_len = len(doc_text)
        while pos < text_len:
            # print doc_text[pos:]
            result = self.match(doc_text, pos)
            if result and (result[0][1] == text_len - 1 or MeshDetect.is_word_sep(doc_text[result[0][1] + 1])):
                # results.append(result)
                span_list.append(result[0])
                id_list.append(result[1])
                pos = result[0][1] + 1
            else:
                while pos < text_len and not MeshDetect.is_word_sep(doc_text[pos]):
                    pos += 1
                pos += 1
        return span_list, id_list

    @staticmethod
    def is_word_sep(ch):
        if ch.isspace():
            return True
        return ch in MeshDetect.word_sep

    @staticmethod
    def load_exclude_words(file_name):
        fin = open(file_name, 'rb')
        fin.readline()
        words_set = set()
        for line in fin:
            words_set.add(line.strip())
        fin.close()
        return words_set
