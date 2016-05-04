import gzip

from meshrecord import MeshRecord


def __load_mids_as_set(mid_list_file):
    keep_mid_set = set()
    fin = open(mid_list_file, 'rb')
    for line in fin:
        keep_mid_set.add(line.strip().split('\t')[0])
    fin.close()
    return keep_mid_set


def __has_alpha(s):
    for ch in s:
        if ch.isalpha():
            return True
    return False


def __load_disamb_wid_file(filename):
    fin = open(filename, 'rb')
    wid_names = dict()
    for line in fin:
        vals = line.strip().split('\t')
        if __has_alpha(vals[0]):
            wid = int(vals[1])
            name_list = wid_names.get(wid, None)
            if not name_list:
                name_list = wid_names[wid] = list()
            name_list.append(vals[0])
    fin.close()

    return wid_names


def gen_dict_with_commonness(name_entity_cnt_file, mid_list_file, candidates_dict_file, num_max_candidates=10):
    keep_mid_set = None
    if mid_list_file:
        keep_mid_set = __load_mids_as_set(mid_list_file)

    fin = open(name_entity_cnt_file, 'rb')
    fout = open(candidates_dict_file, 'wb')
    cur_candidates_dict = dict()
    cur_name = ''
    cur_cnt = 0
    for idx, line in enumerate(fin):
        # if idx == 1000000:
        #     break
        if (idx + 1) % 1000000 == 0:
            print idx + 1

        vals = line.strip().split('\t')

        if len(vals[1]) > 50:
            continue
        if vals[1][0] == '"' or vals[1][0] == "'":
            continue
        if not vals[1][0].isalpha() and not vals[1][0].isdigit() and vals[1][0] != '(':
            continue
        if not __has_alpha(vals[1]):
            continue
        if '<' in vals[1]:
            continue

        if cur_name and vals[1] != cur_name:
            if cur_cnt:
                num_candidates = min(num_max_candidates, len(cur_candidates_dict))
                fout.write('%s\t%d\n' % (cur_name, num_candidates))
                tmp_list = zip(cur_candidates_dict.keys(), cur_candidates_dict.values())
                tmp_list.sort(key=lambda x: -x[1])
                for i in xrange(num_candidates):
                    fout.write('%s\t%f\n' % (tmp_list[i][0], tmp_list[i][1] / float(cur_cnt)))
            cur_candidates_dict = dict()
            cur_cnt = 0

        cur_name = vals[1]

        if not keep_mid_set or vals[0] in keep_mid_set:
            cur_cnt += int(vals[2])
            cur_candidates_dict[vals[0]] = int(vals[2])

    fin.close()
    fout.close()


def gen_mid_list(mid_type_file, mid_list_file):
    mid_head = '<http://rdf.freebase.com/ns/m.'
    type_head = '<http://rdf.freebase.com/ns/'
    mid_head_len = len(mid_head)
    type_head_len = len(type_head)

    fin = gzip.open(mid_type_file, 'rb')
    fout = open(mid_list_file, 'wb')
    for idx, line in enumerate(fin):
        vals = line.strip().split('\t')
        if 'medicine' in vals[2]:
            fout.write('%s\t%s\n' % (vals[0][mid_head_len:-1], vals[2][type_head_len:-1]))
            # print vals[0], vals[2]
        if (idx + 1) % 1000000 == 0:
            print idx + 1
        # if idx == 1000000:
        #     break
    fin.close()
    fout.close()


def gen_single_candidate_dict(dict_with_commonness_file, dst_file):
    fin = open(dict_with_commonness_file, 'rb')
    fout = open(dst_file, 'wb')
    while True:
        line = fin.readline()
        if not line:
            break
        vals = line.strip().split('\t')
        cur_name = vals[0]
        num_candidates = int(vals[1])
        candidate_vals = None
        for i in xrange(num_candidates):
            line = fin.readline()
            if i == 0:
                candidate_vals = line.strip().split('\t')
        if 100 > len(cur_name) > 2 and candidate_vals:
            fout.write('%s\t%s\n' % (cur_name, candidate_vals[0]))

    fin.close()
    fout.close()


def gen_single_candidate_dict_wid(mid_dict_file, mid_wid_file, dst_file):
    mid_wid_dict = dict()
    fin = open(mid_wid_file, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        mid_wid_dict[vals[0]] = vals[1]
    fin.close()

    fin = open(mid_dict_file, 'rb')
    fout = open(dst_file, 'wb')
    for line in fin:
        vals = line.strip().split('\t')
        wid = mid_wid_dict.get(vals[1], None)
        if wid:
            fout.write('%s\t%s\n' % (vals[0], wid))
    fout.close()
    fin.close()


def gen_wid_list(single_candidate_wid_file, mesh_record_file, dst_wid_list_file):
    wid_set = set()
    fin = open(single_candidate_wid_file, 'rb')
    for line in fin:
        vals = line.strip().split('\t')
        wid_set.add(int(vals[1]))
    fin.close()

    mesh_records = MeshRecord.load_mesh_records(mesh_record_file)
    for record in mesh_records.values():
        if record.wid:
            wid_set.add(record.wid)

    fout = open(dst_wid_list_file, 'wb')
    for wid in wid_set:
        fout.write('%d\n' % wid)
    fout.close()


def main():
    mid_type_file = 'e:/el/tmpres/freebase/freebase_types.gz'
    mid_list_file = 'e:/el/tmpres/wiki/demo/dict/mid_list.txt'
    # gen_mid_list(mid_type_file, mid_list_file)

    name_entity_cnt_file = 'd:/data/el/merged_fb_mid_each_alias_cnt.txt'
    candidates_dict_file = 'e:/el/tmpres/demo/dict/candidates_dict_all.txt'
    # gen_dict_with_commonness(name_entity_cnt_file, mid_list_file, candidates_dict_file)
    # gen_dict_with_commonness(name_entity_cnt_file, None, candidates_dict_file)

    single_candidate_file = 'e:/el/tmpres/wiki/demo/dict/single_candidates_dict.txt'
    # gen_single_candidate_dict(candidates_dict_file, single_candidate_file)

    mid_wid_file = 'd:/data/el/mid_to_wid_full_ord_mid.txt'
    single_candidate_wid_file = 'e:/el/tmpres/wiki/demo/dict/single_candidates_wid_dict.txt'
    # gen_single_candidate_dict_wid(single_candidate_file, mid_wid_file, single_candidate_wid_file)

    mesh_record_file = 'd:/data/lab_demo/med_edl_data/record_infos_with_wiki.txt'
    wid_list_file = 'e:/el/tmpres/wiki/demo/wid_list.txt'
    # gen_wid_list(single_candidate_wid_file, mesh_record_file, wid_list_file)

    # merge_to_wiki_dict()

if __name__ == '__main__':
    main()
