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


def pair_matching_between_multi_groups(groups1, groups2):
    pairs = []
    pair_id = 0
    mark = np.full(len(groups2), False)
    for i, g1 in enumerate(groups1):
        for j, g2 in enumerate(groups2):
            if g1.alignment == g2.alignment and abs(g1.compos_number - g2.compos_number) <= 2:
                if match_two_groups(g1, g2, 10):
                    pairs.append([g1, g2])
                    g1.compos_dataframe['pair'] = pair_id
                    g2.compos_dataframe['pair'] = pair_id
                    print('Pair:', g1.id, g2.id)
                    mark[j] = True
                    pair_id += 1
                    break
    return pairs


def pair_matching_within_groups(groups):
    pairs = {}
    pair_id = 0
    # mark = np.full(len(groups), False)
    for i, g1 in enumerate(groups):
        for j in range(i + 1, len(groups)):
            g2 = groups[j]
            if g1.alignment == g2.alignment and abs(g1.compos_number - g2.compos_number) <= 2:
                if match_two_groups(g1, g2, 10):
                    if 'pair' not in g1.compos_dataframe.columns:
                        # hasn't paired yet, creat a new pair
                        g1.compos_dataframe['pair'] = pair_id
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[pair_id] = [g1, g2]
                        pair_id += 1
                    else:
                        # existing pair
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[g1.compos_dataframe.iloc[0]['pair']].append(g2)
    return pairs


def pair_visualization(pairs, img, img_shape, show_method='line'):
    board = img.copy()
    if show_method == 'line':
        for id in pairs:
            pair = pairs[id]
            board = draw.visualize(board, pair[0].compos_dataframe, img_shape, attr='pair', show=False)
            board = draw.visualize(board, pair[1].compos_dataframe, attr='pair')
    elif show_method == 'block':
        for id in pairs:
            pair = pairs[id]
            board = draw.visualize_block(board, pair[0].compos_dataframe, img_shape, attr='pair', show=False)
            board = draw.visualize_block(board, pair[1].compos_dataframe, attr='pair')


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
