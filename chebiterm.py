import re


class ChebiTerm:
    def __init__(self):
        self.chebi_id = -1
        self.name = ''
        self.description = ''
        self.synonyms = list()
        self.isa = list()

    @staticmethod
    def load_obo_file(file_name):
        print 'loading', file_name
        id_start_str = 'id: CHEBI:'
        len_id_start = len(id_start_str)
        name_start_str = 'name: '
        len_name_start = len(name_start_str)
        def_start_str = 'def: '
        synonym_start_str = 'synonym: '
        isa_start_str = 'is_a: CHEBI:'
        len_isa_start = len(isa_start_str)

        chebiterms = dict()

        fin = open(file_name, 'rb')
        for line in fin:
            if line.strip() != '[Term]':
                continue

            chebiterm = ChebiTerm()
            while True:
                line = fin.next()
                if not line or len(line.strip()) == 0:
                    break
                line = line.strip()
                if line.startswith(id_start_str):
                    chebiterm.chebi_id = int(line[len_id_start:])
                elif line.startswith(name_start_str):
                    chebiterm.name = line[len_name_start:]
                elif line.startswith(def_start_str):
                    m = re.search('"(.*?)"', line)
                    chebiterm.description = m.group(1)
                elif line.startswith(synonym_start_str) and 'InChI' not in line:
                    m = re.search('"(.*?)"', line)
                    chebiterm.synonyms.append(m.group(1))
                elif line.startswith(isa_start_str):
                    isa_id = int(line[len_isa_start:])
                    chebiterm.isa.append(isa_id)
            chebiterms[chebiterm.chebi_id] = chebiterm
        fin.close()

        return chebiterms
