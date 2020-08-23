import pandas as pd


def gather_blocks(compos):
    blocks = []
    groups = compos.groupby('pair').groups
    for i in groups:
        if i == -1:
            continue
        block_compos = compos.loc[groups[i]]
        block_compos.rename({"pair": "block"}, axis=1, inplace=True)
        block = Block(i, block_compos)
        blocks.append(block)
    return blocks


class Block:
    def __init__(self, block_id, compos):
        self.id = block_id
        self.compos = compos
        self.list_item_groups = []

    def group_list_items(self):
        groups = self.compos.groupby('list').groups
        for i in groups:
            if i == -1:
                continue
            self.list_item_groups.append(self.compos.loc[groups[i]])

    def calc_list_layout(self):
        for list_group in self.list_item_groups:
            pass
