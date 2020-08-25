import pandas as pd
from obj.Compo_HTML import CompoHTML


def gather_blocks(compos):
    blocks = []
    groups = compos.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        block_compos = compos.loc[groups[i]]
        block_compos.rename({"pair": "list"}, axis=1, inplace=True)
        block_compos.rename({"group": "block"}, axis=1, inplace=True)
        block = Block(i, block_compos)
        blocks.append(block)
    return blocks


class Block:
    def __init__(self, block_id, compos_df):
        self.id = block_id
        self.compos_df = compos_df
        self.compos_html = []
        self.list_item_groups = []

    def group_list_items(self):
        groups = self.compos_df.groupby('list_item').groups
        for i in groups:
            if i == -1:
                continue
            self.list_item_groups.append(self.compos_df.loc[groups[i]])

    def generate_element_html(self):
        for list_item in self.list_item_groups:
            alignment = list_item.iloc[0]['alignment_item']
            if alignment == 'h':
                list_item = list_item.sort_values('column_min')
            if alignment == 'v':
                list_item = list_item.sort_values('row_min')

            for i in range(len(list_item)):
                item = list_item.iloc[i]
                if alignment == 'h':
                    self.compos_html.append(CompoHTML(item, margin_left=int(item['column_min'] - list_item.iloc[i - 1]['column_max'])))
                if alignment == 'v':
                    self.compos_html.append(CompoHTML(item, margin_top=int(item['row_min'] - list_item.iloc[i - 1]['row_max'])))

    def generate_class_css(self):
        pass