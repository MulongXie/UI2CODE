import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
from random import randint as rint
from sklearn.cluster import DBSCAN


class DF_Compos:
    def __init__(self, json_file, img_file):
        self.json_file = json_file
        self.json_data = json.load(open(self.json_file))

        self.compos_json = self.json_data['compos']
        self.compos_dataframe = self.trans_as_df()

        self.img_file = img_file
        self.img = cv2.imread(self.img_file)
        self.img_shape = (self.compos_dataframe.iloc[0].width, self.compos_dataframe.iloc[0].height)

    def trans_as_df(self):
        df = pd.DataFrame(columns=['id', 'column_min', 'column_max', 'row_min', 'row_max',
                                   'center', 'center_column', 'center_row', 'height', 'width', 'area', 'class'])
        for i, compo in enumerate(self.compos_json):
            compo['area'] = compo['height'] * compo['width']
            compo['center'] = ((compo['column_min'] + compo['column_max']) / 2, (compo['row_min'] + compo['row_max']) / 2)
            compo['center_column'] = compo['center'][0]
            compo['center_row'] = compo['center'][1]
            df.loc[i] = compo
        return df

    def select_category(self, categories):
        df = self.compos_dataframe
        return df[df['class'].isin(categories)]

    def DBSCAN_cluster_by_attr(self, attr, eps, min_samples=1, show=True):
        x = np.reshape(list(self.compos_dataframe[attr]), (-1, 1))
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(x)
        tag = 'cluster_' + attr
        self.compos_dataframe[tag] = clustering.labels_
        if show:
            self.visualize(tag)
        return tag

    def DBSCAN_cluster_by_attrs(self, attrs, eps, min_samples=1, show=True):
        x = list(self.compos_dataframe[attrs].values)
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(x)
        tag = 'cluster_' + '_'.join(attrs)
        self.compos_dataframe[tag] = clustering.labels_
        if show:
            self.visualize(tag)
        return tag

    def visualize(self, attr='class', name='board'):
        img = cv2.resize(self.img, self.img_shape)
        board = img.copy()
        for i in range(len(self.compos_dataframe)):
            compo = self.compos_dataframe.iloc[i]
            board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max), (255, 0, 0))
            board = cv2.putText(board, str(compo[attr]), (compo.column_min + 5, compo.row_min + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.imshow(name, board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def visualize_rcolor(self, attr='class', name='board'):
        colors = {}
        img = cv2.resize(self.img, self.img_shape)
        board = img.copy()
        for i in range(len(self.compos_dataframe)):
            compo = self.compos_dataframe.iloc[i]
            if compo[attr] not in colors:
                colors[compo[attr]] = (rint(0, 255), rint(0, 255), rint(0, 255))
            board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max),
                                  colors[compo[attr]], -1)
        cv2.imshow(name, board)
        cv2.waitKey()
        cv2.destroyAllWindows()
