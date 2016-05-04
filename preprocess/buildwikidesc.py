import re
import ioutils

pattern_str = '<doc .*?<title>(.*?)</title>.*?<id>(.*?)</id>.*?' \
              '<text xml:space="preserve">(.*?)</text>.*</doc>'
doc_pattern = re.compile(pattern_str, re.DOTALL)


def next_page(fin):
    page = ''
    flg = False
    # line = fin.readline()
    # while line:
    for line in fin:
        # line = line.decode('utf-8')
        if flg:
            page += line
            if line.strip() == '</doc>':
                return page
        if line.startswith('<doc id='):
            page += line
            flg = True
        # line = fin.readline()
    return None


def strip_doc_text(doc_xml):
    m = doc_pattern.match(doc_xml)
    # print m.group(1)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3).strip()


def find_anchor_text(doc_text):
    anchor_text_set = set()
    miter = re.finditer(r'\[\[(.*?)\|(.*?)\]\]', doc_text)
    for m in miter:
        anchor_text_set.add(m.group(1))
    return anchor_text_set


def get_wanted_part_len_from_wiki(page_text):
    pos = 0
    nl_cnt = 0
    while pos < len(page_text):
        if page_text[pos] == '\n':
            nl_cnt += 1
        if nl_cnt == 5:
            break
        pos += 1

    m = re.search('\n==+.*?==+\n', page_text)
    if m:
        # print m.group()
        pos = min(pos, m.start())
    return pos


def process_file(extracted_wiki_file, id_file, title_file, pos_file, text_file,
                 text_with_links_file, anchors_file, wanted_wid_list_file):
    wanted_wid_set = ioutils.load_int_list_file_to_set(wanted_wid_list_file)

    fin = open(extracted_wiki_file, 'rb')
    fout_id = open(id_file, 'wb')
    fout_title = open(title_file, 'wb')
    fout_pos = open(pos_file, 'wb')
    fout_text = open(text_file, 'wb')
    fout_text_with_links = open(text_with_links_file, 'wb')
    fout_anchors = open(anchors_file, 'wb')

    page_cnt = 0
    while True:
        page_cnt += 1
        if page_cnt % 10000 == 0:
            print page_cnt
        # if page_cnt == 1000:
        #     break

        doc_text = next_page(fin)
        if not doc_text:
            break

        strip_result = strip_doc_text(doc_text)
        if not strip_result:
            continue

        wtitle, wid, wtext = strip_result
        wid = int(wid)
        if wid not in wanted_wid_set:
            continue

        fout_id.write('%d\n' % wid)
        fout_title.write(wtitle + '\n')

        wtext = wtext.replace('\r\n', '\n')
        wanted_len = get_wanted_part_len_from_wiki(wtext)
        wtext = wtext[:wanted_len]

        anchor_text_set = find_anchor_text(wtext)
        for val in anchor_text_set:
            fout_anchors.write(val + '\t')
        fout_anchors.write('\n')

        wtext_no_links = re.sub(r'\[\[(.*?)\|(.*?)\]\]', '\g<2>', wtext)
        num_lines_no_links = wtext_no_links.count('\n')
        num_lines = wtext.count('\n')
        fout_pos.write('%d\t%d\t%d\t%d\n' % (fout_text.tell(), num_lines_no_links + 1,
                                             fout_text_with_links.tell(), num_lines + 1))
        fout_text.write(wtext_no_links + '\n')
        fout_text_with_links.write(wtext + '\n')

    fin.close()

    fout_id.close()
    fout_title.close()
    fout_pos.close()
    fout_text.close()
    fout_text_with_links.close()
    fout_anchors.close()


def gen_wiki_part(wid_file, title_file, pos_file, text_file, anchors_file,
                  wanted_wid_list_file, dst_wid_file, dst_title_file, dst_pos_file,
                  dst_text_file, dst_anchors_file):
    wid_list = ioutils.load_int_list_file_to_list(wid_file)
    pos_list = ioutils.load_int_list_file_to_list(pos_file)
    wanted_wids = ioutils.load_int_list_file_to_set(wanted_wid_list_file)

    dst_wid_list = list()
    dst_pos_list = list()
    fin_title = open(title_file, 'rb')
    fin_text = open(text_file, 'rb')
    fin_anchors = open(text_file, 'rb')

    fout_title = open(title_file, 'wb')
    fout_text = open(text_file, 'wb')
    fout_anchors = open(text_file, 'wb')

    num_wids = len(wid_list)
    for idx in xrange(num_wids):
        next_pos = -1
        if idx < num_wids - 1:
            next_pos = pos_list[idx + 1]
        print next_pos
        cur_text = ''
        while fin_text.tell() < next_pos:
            cur_text += fin_text.readline()
            print fin_text.tell()
        print cur_text
        break

    fin_title.close()
    fin_text.close()
    fin_anchors.close()

    fout_title.close()
    fout_text.close()
    fout_anchors.close()


def main():
    extracted_wiki_file = 'e:/el/tmpres/wiki/enwiki-20150403-text-with-links-main.txt'
    id_file = 'e:/el/tmpres/demo/wiki-med/wid.txt'
    title_file = 'e:/el/tmpres/demo/wiki-med/title.txt'
    pos_file = 'e:/el/tmpres/demo/wiki-med/pos.txt'
    text_file = 'e:/el/tmpres/demo/wiki-med/text.txt'
    text_with_links_file = 'e:/el/tmpres/demo/wiki-med/text-with-links.txt'
    anchors_file = 'e:/el/tmpres/demo/wiki-med/anchors.txt'
    wanted_wid_list_file = 'e:/el/tmpres/demo/wid_list.txt'
    process_file(extracted_wiki_file, id_file, title_file, pos_file, text_file, text_with_links_file, anchors_file,
                 wanted_wid_list_file)

    dst_wid_file = 'e:/el/tmpres/demo/wiki-med/wid.txt'
    dst_title_file = 'e:/el/tmpres/demo/wiki-med/title.txt'
    dst_pos_file = 'e:/el/tmpres/demo/wiki-med/pos.txt'
    dst_text_file = 'e:/el/tmpres/demo/wiki-med/text.txt'
    dst_anchors_file = 'e:/el/tmpres/demo/wiki-med/anchors.txt'
    # gen_wiki_part(id_file, title_file, pos_file, text_file, anchors_file,
    #               wanted_wid_list_file, dst_wid_file, dst_title_file, dst_pos_file,
    #               dst_text_file, dst_anchors_file)


def test():
    pos_file = 'e:/el/tmpres/wiki/demo/pos.txt'
    text_file = 'e:/el/tmpres/demo/wiki-med/text.txt'
    fin = open(text_file, 'rb')
    fin.seek(32654)
    print fin.readline()
    fin.close()

if __name__ == '__main__':
    main()
    # test()
