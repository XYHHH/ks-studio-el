class MeshTree:
    def __init__(self, tree_number_file, mesh_records_dict):
        self.tn_record_dict = dict()
        self.tn_children = dict()
        self.tn_children['r'] = list()  # root

        fin = open(tree_number_file, 'rb')
        for line in fin:
            vals = line.strip().split(';')

            if vals[0] not in mesh_records_dict:
                continue

            self.tn_record_dict[vals[1]] = mesh_records_dict[vals[0]]

            if len(vals[1]) > 3:
                parent_tn = vals[1][:-4]
                cur_children = self.tn_children.get(parent_tn, None)
                if cur_children:
                    cur_children.append(vals[1])
                else:
                    self.tn_children[parent_tn] = [vals[1]]
            else:
                self.tn_children['r'].append(vals[1])
        fin.close()

    def get_parents(self, tree_number):
        parent_list = list()
        tmp_tree_number = tree_number
        while len(tmp_tree_number) > 3:
            tmp_tree_number = tmp_tree_number[:-4]
            parent_list.append((self.tn_record_dict[tmp_tree_number].rid, tmp_tree_number))
        return parent_list
