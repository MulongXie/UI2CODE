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
            compos.loc[compo['id'], 'list'] = compo['id']
            compos.loc[compo['pair_to'], 'list'] = compo['id']
            mark += [compo['id'], compo['pair_to']]

        elif compo['id'] in mark and compo['pair_to'] not in mark:
            index = search_list_item_by_compoid(list_items, compo['id'])
            list_items[index].add_compo(compos.loc[compo['pair_to']])
            compos.loc[compo['pair_to'], 'list'] = index
            mark.append(compo['pair_to'])

        elif compo['id'] not in mark and compo['pair_to'] in mark:
            index = search_list_item_by_compoid(list_items, compo['pair_to'])
            list_items[index].add_compo(compos.loc[compo['id']])
            compos.loc[compo['id'], 'list'] = index
            mark.append(compo['id'])
        # print(compo['id'], compo['pair_to'])
    compos['list'] = compos['list'].astype(int)
    return list_items


class ListItem:
    def __init__(self, alignment, compos):
        self.alignment = alignment
        self.compos = pd.DataFrame(compos)
        self.compos_id = list(self.compos['id'])

    def add_compo(self, compo):
        self.compos.append(compo)
        self.compos_id = list(self.compos['id'])

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.compos, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.compos, img_shape, attr, name)
