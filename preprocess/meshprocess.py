def __load_wid_title_file(wid_title_file):
    wid_title_dict = dict()
    fin = open(wid_title_file, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        wid = int(vals[0])
        wid_title_dict[wid] = vals[1]
    fin.close()

    return wid_title_dict


def __load_wid_title_redirect_file(wid_title_redirect_file):
    fin = open(wid_title_redirect_file, 'rb')
    name_wid_dict = dict()
    for line in fin:
        vals = line.strip().split('\t')
        wid = int(vals[0])
        name_wid_dict[vals[1].lower()] = wid
    fin.close()

    return name_wid_dict


def update_mesh_info_wid():
    mesh_info_file = 'e:/el/tmpres/demo/del-data/records_info_with_wiki.txt'
    wid_title_redirect_file = 'e:/el/tmpres/wiki/dict/wid_title_redirect.txt'
    wid_title_file = 'e:/el/tmpres/wiki/enwiki-20150403-id-title-list.txt'
    new_mesh_info_file = 'e:/el/tmpres/demo/del-data/mesh_info_with_wiki.txt'

    wiki_name_wid_dict = __load_wid_title_redirect_file(wid_title_redirect_file)
    wid_title_dict = __load_wid_title_file(wid_title_file)

    fout = open(new_mesh_info_file, 'wb')
    fin = open(mesh_info_file, 'rb')
    num_records = int(fin.readline().strip())
    for i in xrange(num_records):
        name = fin.next().strip()
        if ',' in name:
            print name
        mesh_id = fin.next().strip()
        wid = fin.next().strip()
        if wid == 'null':
            wid = 0
        else:
            wid = int(wid)
        wiki_title = fin.next().strip()
        fin.next()  # skip mesh description

        new_wid = wiki_name_wid_dict.get(name.lower(), 0)

        num_terms = int(fin.next().strip())
        terms = list()
        for j in xrange(num_terms):
            term = fin.next().strip()
            terms.append(term)
            if not new_wid:
                new_wid = wiki_name_wid_dict.get(term.lower(), 0)

        fout.write('%s\n%s\n' % (name, mesh_id))
        if wid:
            new_title = wid_title_dict[new_wid]
            fout.write('%d\n%s\n' % (new_wid, new_title))
        else:
            fout.write('null\nnull\n')

        num_mns = int(fin.next().strip())
        for j in xrange(num_mns):
            mn = fin.next()

        # if wid != new_wid:
        #     if new_wid == 0:
        #         new_title = ''
        #     else:
        #         new_title = wid_title_dict[new_wid]
        #     print name
        #     print wid, wiki_title, new_wid, new_title
    fin.close()
    fout.close()


def main():
    update_mesh_info_wid()

if __name__ == '__main__':
    main()
