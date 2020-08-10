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


def pair_matching(groups1, groups2):
    pairs = []
    mark = np.full(len(groups2), False)
    for i, g1 in enumerate(groups1):
        for j, g2 in enumerate(groups2):
            if g1.alignment == g2.alignment and abs(g1.compos_number - g2.compos_number) <= 2:
                if match_two_groups(g1, g2, 10):
                    pairs.append([g1, g2])
                    print('Pair:', g1.id, g2.id)
                    mark[j] = True
                    break
    return pairs


def pair_visualization(pairs, img, img_shape, show_method='line'):
    if show_method == 'line':
        for pair in pairs:
            board = draw.visualize(img, pair[0].compos_dataframe, img_shape, show=False)
            draw.visualize(board, pair[1].compos_dataframe)
    elif show_method == 'block':
        for pair in pairs:
            board = draw.visualize_block(img, pair[0].compos_dataframe, img_shape, show=False)
            draw.visualize_block(board, pair[1].compos_dataframe)


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
