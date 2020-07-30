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

    def reload_compos(self, json_file=None):
        if json_file is None:
            json_file = self.json_file
        self.json_data = json.load(open(json_file))
        self.compos_json = self.json_data['compos']
        self.compos_dataframe = self.trans_as_df()

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

    def select_by_class(self, categories, replace=False):
        df = self.compos_dataframe
        df = df[df['class'].isin(categories)]
        if replace:
            self.compos_dataframe = df
        else:
            return df

    def cluster_dbscan_by_attr(self, attr, eps, min_samples=1, show=True, show_method='line'):
        x = np.reshape(list(self.compos_dataframe[attr]), (-1, 1))
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(x)
        tag = 'cluster_' + attr
        self.compos_dataframe[tag] = clustering.labels_
        if show:
            if show_method == 'line':
                self.visualize(tag, tag)
            elif show_method == 'block':
                self.visualize_block(tag, tag)

    def cluster_dbscan_by_attrs(self, attrs, eps, min_samples=1, show=True, show_method='line'):
        x = list(self.compos_dataframe[attrs].values)
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(x)
        tag = 'cluster_' + '_'.join(attrs)
        self.compos_dataframe[tag] = clustering.labels_
        if show:
            if show_method == 'line':
                self.visualize(tag, tag)
            elif show_method == 'block':
                self.visualize_block(tag, tag)

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

    def visualize_block(self, attr='class', name='board'):
        colors = {}
        img = cv2.resize(self.img, self.img_shape)
        board = img.copy()
        for i in range(len(self.compos_dataframe)):
            compo = self.compos_dataframe.iloc[i]
            if compo[attr] == -1:
                board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max),
                                      (rint(0, 255), rint(0, 255), rint(0, 255)), -1)
                continue
            elif compo[attr] not in colors:
                colors[compo[attr]] = (rint(0, 255), rint(0, 255), rint(0, 255))
            board = cv2.rectangle(board, (compo.column_min, compo.row_min), (compo.column_max, compo.row_max),
                                      colors[compo[attr]], -1)
            board = cv2.putText(board, str(compo[attr]), (compo.column_min + 5, compo.row_min + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        cv2.imshow(name, board)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def group_by_clusters(self, cluster, new_groups=True, show=True, show_method='block'):
        compos = self.compos_dataframe
        if 'group' not in compos.columns or new_groups:
            self.compos_dataframe['group'] = -1
            group_id = 0
        else:
            group_id = compos['group'].max()

        groups = self.compos_dataframe.groupby(cluster).groups
        for i in groups:
            if len(groups[i]) > 1:
                self.compos_dataframe.loc[list(groups[i]), 'group'] = group_id
                group_id += 1
        if show:
            name = cluster if type(cluster) != list else '+'.join(cluster)
            if show_method == 'line':
                self.visualize(attr='group', name=name)
            elif show_method == 'block':
                self.visualize_block(attr='group', name=name)

    def close_distance_to_cluster_mean_area(self, compo_index, cluster1, cluster2):
        compos = self.compos_dataframe
        compo = compos.loc[compo_index]
        mean_area1 = compos[compos[cluster1] == compo[cluster1]]['area'].mean()
        mean_area2 = compos[compos[cluster2] == compo[cluster2]]['area'].mean()

        compo_area = compo['area']
        if abs(compo_area - mean_area1) < abs(compo_area - mean_area2):
            return 1
        return 2

    def group_by_clusters_conflict(self, cluster, prev_cluster, show=True, show_method='block'):
        compos = self.compos_dataframe
        group_id = compos['group'].max()

        groups = self.compos_dataframe.groupby(cluster).groups
        for i in groups:
            if len(groups[i]) > 1:
                member_num = len(groups[i])
                for j in list(groups[i]):
                    if compos.loc[j, 'group'] == -1:
                        compos.loc[j, 'group'] = group_id
                    # conflict raised if a component can be grouped into multiple groups
                    # then double check it by distance to the mean area of the groups
                    else:
                        # keep in the previous group if the it is the only member in a new group
                        if member_num <= 1:
                            continue

                        # close to the current cluster
                        if self.close_distance_to_cluster_mean_area(j, cluster, prev_cluster) == 1:
                            compos.loc[j, 'group'] = group_id
                        else:
                            member_num -= 1
                group_id += 1

        if show:
            name = cluster if type(cluster) != list else '+'.join(cluster)
            if show_method == 'line':
                self.visualize(attr='group', name=name)
            elif show_method == 'block':
                self.visualize_block(attr='group', name=name)
