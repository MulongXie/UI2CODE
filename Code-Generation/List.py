import pandas as pd
import draw


def match_list_item_by_compoid(list_items, compo_id):
    """
        list_items: dictionary => {id of first compo: ListItem}
    """
    for i in list_items:
        if compo_id in list_items[i].compos_id:
            return i


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
