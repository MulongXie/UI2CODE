import pandas as pd
from obj.CSS import CSS


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

    def get_groups_layouts(self):
        compos = self.compos_df
        groups = compos.groupby('group').groups
        layouts = []
        if self.list_alignment == 'v':
            for i in groups:
                layouts.append((i, compos.loc[groups[i], 'column_min'].min(), compos.loc[groups[i], 'column_max'].max()))
        elif self.list_alignment == 'h':
            for i in groups:
                layouts.append(
                    (i, compos.loc[groups[i], 'row_min'].min(), compos.loc[groups[i], 'row_max'].max()))
        layouts = sorted(layouts, key=lambda k: k[1])
        return layouts

    def generate_element_css(self):
        pass

    def generate_list_css(self):
        css = {}
        if self.list_type == 'multiple':
            groups_layouts = self.get_groups_layouts()
            if self.list_alignment == 'v':
                for i in range(1, len(groups_layouts)):
                    css[groups_layouts[i][0]] = CSS('.' + groups_layouts[i][0], margin_left=str(int(groups_layouts[i][1] - groups_layouts[i - 1][2])))
            if self.list_alignment == 'h':
                for i in range(1, len(groups_layouts)):
                    css[groups_layouts[i][0]] = CSS('.' + groups_layouts[i][0], margin_top=str(int(groups_layouts[i][1] - groups_layouts[i - 1][2])))
        return css
