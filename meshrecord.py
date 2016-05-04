class MeshRecord:
    def __init__(self):
        self.rid = None
        self.name = None
        self.wid = None
        self.wiki_title = None
        self.mesh_desc = None
        self.terms = None
        self.mns = None

    @staticmethod
    def load_mesh_records(record_file):
        print 'loading', record_file
        records = dict()
        fin = open(record_file, 'rb')
        num_records = int(fin.readline().strip())
        for i in xrange(num_records):
            rec = MeshRecord()
            rec.name = fin.readline().strip()
            rec.rid = fin.readline().strip()
            wid = fin.readline().strip()
            rec.wid = None if wid == 'null' else int(wid)
            rec.wiki_title = fin.readline().strip()
            rec.mesh_desc = fin.readline().strip()

            rec.terms = list()
            num_terms = fin.readline().strip()
            # num_terms = int(fin.readline().strip())
            num_terms = int(num_terms)
            for j in xrange(num_terms):
                rec.terms.append(fin.readline().strip())

            rec.mns = list()
            num_mns = int(fin.readline().strip())
            for j in xrange(num_mns):
                rec.mns.append(fin.readline().strip())

            records[rec.rid] = rec

        fin.close()

        return records
