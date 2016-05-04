import math
from nltk import word_tokenize


class TfIdf:
    def __init__(self, word_idf_file):
        print 'loading', word_idf_file
        self.word_idx = dict()
        self.idf_values = list()
        fin = open(word_idf_file, 'rb')
        for idx, line in enumerate(fin):
            vals = line.strip().split('\t')
            self.word_idx[vals[0]] = idx
            self.idf_values.append(float(vals[1]))
        fin.close()

    def get_idf(self, word):
        idx = self.word_idx.get(word.lower(), -1)
        if idx > -1:
            return self.idf_values[idx]

    def get_tfidf(self, words):
        bow = self.get_bow(words)
        num_words = 0.0
        for idx, cnt in bow:
            num_words += cnt

        tfidf_vec = list()
        for idx, cnt in bow:
            tfidf_vec.append((idx, cnt / num_words * self.idf_values[idx]))
        return tfidf_vec

    def get_bow(self, words):
        bow = dict()
        for word in words:
            if len(word) > 0:
                # idx = self.word_idx[word.lower()]
                idx = self.word_idx.get(word.lower(), -1)
                if idx > 0:
                    cnt = bow.get(idx, 0)
                    bow[idx] = cnt + 1

        bow = bow.items()
        bow.sort(key=lambda x: x[0])
        return bow

    def get_tfidf_from_text(self, text):
        words = word_tokenize(text)
        return self.get_tfidf(words)

    @staticmethod
    def sim(vec0, vec1):
        if len(vec0) == 0 or len(vec1) == 0:
            return 0.0

        norm0 = TfIdf.__norm(vec0)
        norm1 = TfIdf.__norm(vec1)

        dp = 0
        pos1 = 0
        for pos0, tup0 in enumerate(vec0):
            while pos1 < len(vec1) and vec1[pos1][0] < tup0[0]:
                pos1 += 1
            if pos1 == len(vec1):
                break
            if vec1[pos1][0] == tup0[0]:
                dp += vec1[pos1][1] * tup0[1]
        return dp / norm0 / norm1

    @staticmethod
    def __norm(vec):
        rslt = 0
        for idx, val in vec:
            rslt += val * val
        return math.sqrt(rslt)
