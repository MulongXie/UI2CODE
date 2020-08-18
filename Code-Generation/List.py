import pandas as pd
import draw


def search_list_item_by_compoid(list_items, compo_id):
    """
        list_items: dictionary => {id of first compo: ListItem}
    """
    for i in list_items:
        if compo_id in list_items[i].compos_id:
            return i


def gather_list_items(compos):
    list_items = {}
    mark = []
    for i in range(len(compos)):
        compo = compos.iloc[i]
        # new item
        if compo['id'] not in mark and compo['pair_to'] not in mark:
            compo_paird = compos.loc[compo['pair_to']]
            item = ListItem(compo['alignment'], [compo, compo_paird])
            list_items[compo['id']] = item
            mark += [compo['id'] , compo['pair_to']]

        elif compo['id'] in mark and compo['pair_to'] not in mark:
            index = search_list_item_by_compoid(list_items, compo['id'])
            list_items[index].add_compo(compos.loc[compo['pair_to']])
            mark.append(compo['pair_to'])

        elif compo['id'] not in mark and compo['pair_to'] in mark:
            index = search_list_item_by_compoid(list_items, compo['pair_to'])
            list_items[index].add_compo(compos.loc[compo['id']])
            mark.append(compo['id'])
        # print(compo['id'], compo['pair_to'])
    return list_items


class ListItem:
    def __init__(self, alignment, compos, ids=None):
        self.alignment = alignment
        self.compos = compos
        self.compos_id = ids if ids is not None else self.get_compos_id()

    def get_compos_id(self):
        return [compo['id'] for compo in self.compos]

    def add_compo(self, compo):
        self.compos.append(compo)
        self.compos_id = self.get_compos_id()

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.elements, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.elements, img_shape, attr, name)
