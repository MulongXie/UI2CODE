import pandas as pd
import cv2
import numpy as np

import draw
from Group import *


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
    pairs = {}
    pair_id = 0
    for i, g1 in enumerate(groups1):
        for j, g2 in enumerate(groups2):
            if g1.alignment == g2.alignment and abs(g1.compos_number - g2.compos_number) <= 2:
                if match_two_groups(g1, g2, 10):
                    if 'pair' not in g1.compos_dataframe.columns:
                        # hasn't paired yet, creat a new pair
                        pair_id += 1
                        g1.compos_dataframe['pair'] = pair_id
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[pair_id] = [g1, g2]
                    else:
                        # existing pair
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[g1.compos_dataframe.iloc[0]['pair']].append(g2)
    return pairs


def pair_matching_within_groups(groups, new_pairs=True):
    pairs = {}
    pair_id = 0
    mark = np.full(len(groups), False)
    if new_pairs:
        for group in groups:
            if 'pair' in group.compos_dataframe.columns:
                group.compos_dataframe.drop('pair', axis=1, inplace=True)
    for i, g1 in enumerate(groups):
        for j in range(i + 1, len(groups)):
            g2 = groups[j]
            if g1.alignment == g2.alignment and abs(g1.compos_number - g2.compos_number) <= 2:
                if match_two_groups(g1, g2, 10):
                    if not mark[i]:
                        # hasn't paired yet, creat a new pair
                        pair_id += 1
                        g1.compos_dataframe['pair'] = pair_id
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[pair_id] = [g1, g2]
                        mark[i] = True
                        mark[j] = True
                    else:
                        # existing pair
                        g2.compos_dataframe['pair'] = pair_id
                        pairs[g1.compos_dataframe.iloc[0]['pair']].append(g2)
                        mark[j] = True
    no_pairs = []
    for i in range(len(mark)):
        if not mark[i]:
            no_pairs.append(groups[i])

    return pairs, no_pairs


def pair_visualization(pairs, img, img_shape, show_method='line'):
    board = img.copy()
    if show_method == 'line':
        for id in pairs:
            pair = pairs[id]
            for p in pair:
                board = draw.visualize(board, p.compos_dataframe, img_shape, attr='pair', show=False)
    elif show_method == 'block':
        for id in pairs:
            pair = pairs[id]
            for p in pair:
                board = draw.visualize_block(board, p.compos_dataframe, img_shape, attr='pair', show=False)
    cv2.imshow('pairs', board)
    cv2.waitKey()
    cv2.destroyAllWindows()


def pair_cvt_df(pairs):
    df = pd.DataFrame()
    for i in pairs:
        pair = pairs[i]
        for group in pair:
            df = df.append(group.compos_dataframe, sort=False)
    df = df.sort_index()
    return df

