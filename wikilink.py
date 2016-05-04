import cPickle
from bisect import bisect_left
from preprocess.tfidf import TfIdf


class WikiLink:
    def __init__(self, candidates_file, wiki_info, tfidf=None):
        print 'loading', candidates_file
        fin = open(candidates_file, 'rb')
        nc_dict = cPickle.load(fin)
        fin.close()

        self.name_list = nc_dict['names']
        self.beg_indices = nc_dict['beg-indices']
        self.candidates = nc_dict['candidates']
        self.cnts = nc_dict['cnts']
        self.wiki_info = wiki_info
        self.tfidf = tfidf

    def link(self, sname):
        pos = bisect_left(self.name_list, sname)
        if self.name_list[pos] != sname:
            return -1
        return self.candidates[self.beg_indices[pos]]

    def link_all(self, text, mentions):
        if not self.tfidf:
            return None

        name_expantion_dict = dict()

        name_results = dict()
        for i, mention in enumerate(mentions):
            if not mention.mesh_id and mention.chebi_id < 0:
                cur_name = text[mention.span[0]:mention.span[1] + 1]
                if i > 0:
                    exp_name = WikiLink.__try_expand(text, mention, mentions[i - 1])
                    if exp_name:
                        name_expantion_dict[cur_name.lower()] = exp_name.lower()
                name_results[cur_name.lower()] = -1
        # print name_expantion_dict

        context_tfidf = self.tfidf.get_tfidf_from_text(text)
        for name in name_results.keys():
            name = name.lower()
            link_result = self.link_with_context(name, context_tfidf)
            name_results[name] = link_result
            # print name, link_result

        for mention in mentions:
            if (not mention.mesh_id) and mention.chebi_id < 0:
                cur_name = text[mention.span[0]:mention.span[1] + 1].lower()
                exp_name = name_expantion_dict.get(cur_name, None)
                if exp_name:
                    cur_name = exp_name
                mention.wid = name_results.get(cur_name, -1)
                # print cur_name, mention.wid

    def link_with_context(self, sname, context_tfidf):
        if not self.tfidf:
            return -1

        pos = bisect_left(self.name_list, sname)
        if self.name_list[pos] != sname:
            return -1
        beg_idx = self.beg_indices[pos]
        if pos == len(self.beg_indices) - 1:
            end_idx = len(self.candidates)
        else:
            end_idx = self.beg_indices[pos + 1]

        result_wid = self.candidates[beg_idx]

        if end_idx == beg_idx + 1:
            wiki_info = self.wiki_info.get_info(result_wid)
            if wiki_info and wiki_info[1]:
                if 'may refer to' in wiki_info[1] or 'may stand for' in wiki_info[1]:
                    return -1
            return result_wid

        sum_cnts = 0.0
        for i in xrange(beg_idx, end_idx):
            sum_cnts += self.cnts[i]

        max_score = -1
        for i in xrange(beg_idx, end_idx):
            cur_wid = self.candidates[i]
            wiki_info = self.wiki_info.get_info(cur_wid)
            if wiki_info and wiki_info[1]:
                if 'may refer to' in wiki_info[1] or 'may stand for' in wiki_info[1]:
                    continue

                candidate_tfidf = self.tfidf.get_tfidf_from_text(wiki_info[1].decode('utf-8'))
                sim = TfIdf.sim(candidate_tfidf, context_tfidf)
                # if sname == 'elisa' or sname == 'sfn':
                #     print cur_wid, wiki_info[0], sim, self.cnts[i], sum_cnts, self.cnts[i] / sum_cnts
                # print cur_wid, wiki_info[0], sim
                # score = sim + 0.0 * self.cnts[i] / sum_cnts
                score = sim
                if score > max_score:
                    max_score = score
                    result_wid = cur_wid

        return result_wid

    @staticmethod
    def __try_expand(text, mention, prev_mention):
        if mention.span[0] == 0 or mention.span[1] == len(text) - 1:
            return None
        if text[mention.span[0] - 1] != '(' or text[mention.span[1] + 1] != ')':
            return None
        if prev_mention.span[1] + 3 < mention.span[0]:
            return None

        cur_name = text[mention.span[0]:mention.span[1] + 1]
        prev_name = text[prev_mention.span[0]:prev_mention.span[1] + 1]
        if cur_name.isupper() and WikiLink.__is_acronym(cur_name, prev_name):
            return prev_name.lower()

    @staticmethod
    def __is_acronym(name0, name1):
        if name0[0].lower() != name1[0].lower():
            return False

        pos = 0
        len1 = len(name1)
        for ch in name0:
            while pos < len1:
                if ch.lower() == name1[pos].lower():
                    pos += 1
                    break
                pos += 1
            if pos == len1:
                return False
        return True
