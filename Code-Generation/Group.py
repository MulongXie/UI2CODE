import pandas as pd
import numpy as np

import draw


def match_two_groups(g1, g2, max_pos_bias):
    assert g1.alignment == g2.alignment
    alignment = g1.alignment
    g1 = g1.compos_dataframe
    g2 = g2.compos_dataframe
    match_num = 0
    if alignment == 'h':
        for i in range(len(g1)):
            c1 = g1.iloc[i]
            for j in range(len(g2)):
                c2 = g2.iloc[j]
                if abs(c1.column_min - c2.column_min) < max_pos_bias:
                    match_num += 1
                    break
    elif alignment == 'v':
        for i in range(len(g1)):
            c1 = g1.iloc[i]
            for j in range(len(g2)):
                c2 = g2.iloc[j]
                if abs(c1.row_min - c2.row_min) < max_pos_bias:
                    match_num += 1
                    break

    if match_num >= min(len(g1), len(g2)):
        return True
    return False


class Group:
    def __init__(self, id, category, alignment, compos_ids, compos_dataframe):
        self.id = id
        self.category = category
        self.alignment = alignment
        self.compos_ids = compos_ids
        self.compos_dataframe = compos_dataframe
        self.compos_number = len(self.compos_ids)

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.compos_dataframe, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.compos_dataframe, img_shape, attr, name)
