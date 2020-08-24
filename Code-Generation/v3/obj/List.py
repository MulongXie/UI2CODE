import pandas as pd


def gather_lists(compos):
    lists = []
    groups = compos.groupby('pair').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(compos.loc[groups[i]], 'multiple', compos.loc[groups[i][0]]['alignment_list']))
        compos = compos.drop(list(groups[i]))

    groups = compos.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(compos.loc[groups[i]], 'single', compos.loc[groups[i][0]]['alignment_list']))
        compos = compos.drop(list(groups[i]))
    return lists


class List:
    def __init__(self, compos_df, list_type, list_alignment):
        self.compos_df = compos_df
        self.list_type = list_type
        self.list_alignment = list_alignment

    def group_layout(self):
        groups = self.compos_df.groupby('group').groups
        layouts = []
        for i in groups:
            layouts.append((i, self.compos_df.loc[groups[i], 'column_min'].min()))
        print(layouts)

    def generate_item_css(self):
        if self.list_type == 'multiple':
            pass
