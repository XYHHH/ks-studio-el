from bisect import bisect_left
import cPickle


class WikiInfo:
    def __init__(self, wiki_info_file, links_file, description_file):
        print 'loading', wiki_info_file

        if wiki_info_file.endswith('pkl'):
            self.__load_wiki_info_from_pkl(wiki_info_file)
        else:
            self.__load_wiki_info_from_text_file(wiki_info_file)

        self.fin_description = open(description_file, 'rb')

        self.links = list()
        fin_links = open(links_file, 'rb')
        for line in fin_links:
            self.links.append(line.strip())
        fin_links.close()

    def get_info(self, wid):
        pos = bisect_left(self.wids, wid)
        if self.wids[pos] != wid:
            return None, None, None

        text_pos = self.text_positions[pos]
        self.fin_description.seek(text_pos)
        description = self.fin_description.readline().strip()
        return self.titles[pos], description, self.links[pos].split('\t')

    def __load_wiki_info_from_text_file(self, filename):
        self.wids = list()
        self.titles = list()
        self.text_positions = list()

        fin_info = open(filename, 'rb')
        for line in fin_info:
            wid = int(line.strip())
            title = fin_info.next().strip()
            pos_vals = fin_info.next().strip().split('\t')

            self.wids.append(wid)
            self.titles.append(title)
            self.text_positions.append(int(pos_vals[0]))
        fin_info.close()

    def __load_wiki_info_from_pkl(self, filename):
        fin = open(filename, 'rb')
        info_dict = cPickle.load(fin)
        fin.close()
        self.wids = info_dict['wids']
        self.titles = info_dict['titles']
        self.text_positions = info_dict['text_pos']
