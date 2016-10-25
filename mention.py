class Mention:
    def __init__(self, span=(), mtype='', mesh_id='', wid=-1, chebi_id=-1):
        self.span = span
        self.mtype = mtype
        self.mesh_id = mesh_id
        self.wid = wid
        self.candidates = list()
        self.chebi_id = chebi_id
        self.name = ''

    @staticmethod
    def find_conflict_mention(cur_mention, mention_list):
        for mention in mention_list:
            if not (cur_mention.span[1] < mention.span[0] or cur_mention.span[0] > mention.span[1]):
                return mention
        return None

    @staticmethod
    def merge_mention_list(new_list, dst_list):
        for mention in new_list:
            conflict_mention = Mention.find_conflict_mention(mention, dst_list)
            if conflict_mention:
                if mention.mtype == 'Disease' or mention.mtype == 'Chemical':
                    conflict_mention.mtype = mention.mtype
            else:
                dst_list.append(mention)
