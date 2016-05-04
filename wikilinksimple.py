class WikiLinkSimple:
    def __init__(self, candidates_file, multi_candidates=True):
        print 'loading', candidates_file
        if multi_candidates:
            self.__load_candidates_file_multi(candidates_file)
        else:
            self.__load_candidates_file_single(candidates_file)

    def link(self, sname):
        return self.candidates_dict.get(sname, -1)

    def __load_candidates_file_multi(self, filename):
        self.candidates_dict = dict()
        fin = open(filename)
        for line in fin:
            vals = line.strip().split('\t')
            num_candidates = int(vals[1])
            for i in xrange(num_candidates):
                candidate_line = fin.next()
                if i == 0:
                    candidate_vals = candidate_line.strip().split('\t')
                    self.candidates_dict[vals[0]] = int(candidate_vals[0])
        fin.close()

    def __load_candidates_file_single(self, filename):
        self.candidates_dict = dict()
        fin = open(filename, 'rb')
        for line in fin:
            vals = line.strip().split('\t')
            self.candidates_dict[vals[0]] = int(vals[1])
            name_lower = vals[0].lower()
            if name_lower not in self.candidates_dict:
                self.candidates_dict[name_lower] = int(vals[1])
        fin.close()
