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
    # df = df[(df['class'] == 'Background') | (df['class'] == 'TextView')]
    df = df[df['class'] != 'TextView']
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
    area = np.reshape(list(compos['area']), (-1, 1))
    clustering = DBSCAN(eps=200, min_samples=1).fit(area)
    compos['cluster_area'] = clustering.labels_
    draw(org, compos, 'cluster_area', 'area')

    # clustering by position of center
    center = np.reshape(list(compos['center']), (len(compos), -1))
    x = np.reshape(center[:, 0], (-1, 1))
    y = np.reshape(center[:, 1], (-1, 1))
    clustering = DBSCAN(eps=5, min_samples=1).fit(x)
    compos['cluster_x'] = clustering.labels_
    draw(org, compos, 'cluster_x', 'x')
    clustering = DBSCAN(eps=5, min_samples=1).fit(y)
    compos['cluster_y'] = clustering.labels_
    draw(org, compos, 'cluster_y', 'y')


def group_compos_by_area_and_pos(org, compos):
    g1 = compos.groupby(['cluster_area', 'cluster_x']).groups
    g2 = compos.groupby(['cluster_area', 'cluster_y']).groups

    group_id = 0
    compos['group'] = -1
    for i in g1:
        if len(g1[i]) > 1:
            compos.loc[list(g1[i]), 'group'] = group_id
            group_id += 1

    for i in g2:
        if len(g2[i]) > 1:
            compos.loc[list(g2[i]), 'group'] = group_id
            group_id += 1

    draw_rcolor(org, compos, 'group', 'group')


compos = read_compos()
org = cv2.imread('9.png')
dbscan_clusterig(org, compos)
group_compos_by_area_and_pos(org, compos)