import pandas as pd
import draw


class Block:
    def __init__(self, block_id, compos, list_items=None):
        self.id = block_id
        self.compos = compos
        self.list_items = list_items if list_items is not None else []

    def add_list_item(self, list_item):
        self.list_items.append(list_item)

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.compos, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.compos, img_shape, attr, name)
