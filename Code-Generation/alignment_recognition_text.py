import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
from random import randint as rint
from sklearn.cluster import DBSCAN


def read_compos(file='compo.json'):
    compos = json.load(open(file))['compos']
    df = pd.DataFrame(columns=['id', 'column_min', 'column_max', 'row_min', 'row_max', 'center', 'height', 'width', 'area', 'class'])
    for i, compo in enumerate(compos):
        compo['area'] = compo['height'] * compo['width']
        compo['center'] = ((compo['column_min'] + compo['column_max'])/2, (compo['row_min'] + compo['row_max'])/2)
        df.loc[i] = compo
    df = df[(df['class'] == 'Background') | (df['class'] == 'Text')]
    # df = df[df['class'] != 'TextView']
    return df


def draw_rcolor(org, compos, opt='class', name='board'):
    colors = {}

    img_h, img_w = compos.iloc[0].height, compos.iloc[0].width
    img = cv2.resize(org, (img_w, img_h))
    board = img.copy()
    for i in range(len(compos)):
        compo = compos.iloc[i]
        if compo[opt] not in colors:
            colors[compo[opt]] = (rint(0, 255), rint(0, 255), rint(0, 255))

        board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max),
                              colors[compo[opt]], -1)

    cv2.imshow(name, board)
    cv2.waitKey()
    cv2.destroyAllWindows()


def draw(org, compos, opt='class', name='board'):
    img_h, img_w = compos.iloc[0].height, compos.iloc[0].width
    img = cv2.resize(org, (img_w, img_h))
    board = img.copy()
    for i in range(len(compos)):
        compo = compos.iloc[i]
        board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max), (255, 0, 0))
        board = cv2.putText(board, str(compo[opt]), (compo.column_min + 5, compo.row_min + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    cv2.imshow(name, board)
    cv2.waitKey()
    cv2.destroyAllWindows()


def dbscan_clusterig(org, compos):
    # clustering by area
    #     area = np.reshape(list(compos['width']), (-1, 1))
    #     clustering = DBSCAN(eps=15, min_samples=1).fit(area)
    #     compos['cluster_width'] = clustering.labels_
    #     draw_rcolor(org, compos, 'cluster_width', 'width')

    # clustering by top left points
    top = np.reshape(list(compos['row_min']), (-1, 1))
    clustering = DBSCAN(eps=5, min_samples=1).fit(top)
    compos['cluster_top'] = clustering.labels_
    draw(org, compos, 'cluster_top', 'top')

    left = np.reshape(list(compos['column_min']), (-1, 1))
    clustering = DBSCAN(eps=5, min_samples=1).fit(left)
    compos['cluster_left'] = clustering.labels_
    draw(org, compos, 'cluster_left', 'left')

    # clustering by area
#     x = list(compos[['width', 'height']].values)
#     x = np.reshape(x, (len(x), -1))
#     clustering = DBSCAN(eps=15, min_samples=1).fit(x)
#     compos['cluster_shape'] = clustering.labels_
#     draw_rcolor(org, compos, 'cluster_shape', 'shape')


def group_by_mean_area(compos, index):
    compo = compos.loc[index]
    area_mean_top = compos[compos['cluster_top'] == compo['cluster_top']]['area'].mean()
    area_mean_left = compos[compos['cluster_left'] == compo['cluster_left']]['area'].mean()

    compo_area = compo['area']
    # depends on horizontal cluster
    if abs(compo_area - area_mean_top) < abs(compo_area - area_mean_left):
        return 0
    # depends on vertical cluster
    return 1


def group_compos_by_top_left(org, compos):
    group_id = 0
    compos['group'] = -1

    # group by horizontal alignment (top)
    g1 = compos.groupby(['cluster_top']).groups
    for i in g1:
        if len(g1[i]) > 1:
            compos.loc[list(g1[i]), 'group'] = group_id
            group_id += 1

    # group by vertical alignment (left)
    g2 = compos.groupby(['cluster_left']).groups
    for i in g2:
        if len(g2[i]) > 1:
            for j in list(g2[i]):
                if compos.loc[j, 'group'] == -1:
                    compos.loc[j, 'group'] = group_id

                # conflict raised if a component can be clustered both horizontally(top) and vertically(left)
                # then double check it by area with the clustering average
                else:
                    # subject to horizontal alignment
                    if group_by_mean_area(compos, j) == 0:
                        continue
                    # subject to vertical alignment
                    else:
                        compos.loc[j, 'group'] = group_id
            group_id += 1

    draw_rcolor(org, compos, 'group', 'group')


compos = read_compos()
org = cv2.imread('9.png')
dbscan_clusterig(org, compos)
group_compos_by_top_left(org, compos)
