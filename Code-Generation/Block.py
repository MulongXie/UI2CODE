import pandas as pd
import draw


class Block:
    def __init__(self, compos):
        self.compos = compos
        self.list_items = None

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.compos, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.compos, img_shape, attr, name)
