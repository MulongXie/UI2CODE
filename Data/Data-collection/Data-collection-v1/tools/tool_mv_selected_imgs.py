import pandas as pd
import glob
from os.path import join as pjoin
from shutil import copy
import os

# dataset1: ip500 0-302 in keras-yolo3_new/data
# dataset2: page10000 303-1103 in keras-yolo3_new/data
stamp = 302
start_point = 4402 - stamp
# original path of datasets
img_root = 'E:/Mulong/Datasets/dataset_webpage/page10000/ip_img_segment/'
label_root = 'E:/Mulong/Datasets/dataset_webpage/page10000/relabel/'


def move_selected_img(stamp, start_point, img_root, label_root):
    if not os.path.exists(img_root) or not os.path.exists(label_root):
        print('No such root')
        return
    # new_root = pjoin(img_root.replace('img_segment', 'img_segment_relabeled'))
    new_root = 'E:\\Mulong\\GoogleDrive\\research\\code\\keras-yolo3_new\\data'
    label_paths = glob.glob(pjoin(label_root, '*.csv'))
    label_paths.sort(key=lambda x: int(x.split('\\')[-1][:-4]))

    for label_path in label_paths:
        index = label_path.split('\\')[-1][:-4]
        if int(index) <= start_point:
            continue
        label = pd.read_csv(label_path)
        pre_seg_no = -1
        for i in range(len(label)):
            l = label.iloc[i]
            seg_no = l['segment_no']
            if seg_no == pre_seg_no:
                continue
            else:
                pre_seg_no = seg_no
            old_path = pjoin(img_root, index, str(int(seg_no)) + '.png')
            new_path = pjoin(new_root, str(int(index) + stamp))
            if not os.path.exists(new_path):
                os.mkdir(new_path)
            new_path = pjoin(new_path, str(int(seg_no)) + '.png')
            copy(old_path, new_path)


# Move relabeled images
move_selected_img(stamp, start_point, img_root, label_root)


def label_convert(stamp, start_point, label_root, img_root):
    def box_convert(label):
        x_min = label['bx']
        y_min = label['by']
        x_max = x_min + label['bw']
        y_max = y_min + label['bh']
        if label['element'] == 'button':
            element = '0'
        elif label['element'] == 'input':
            element = '1'
        elif label['element'] == 'select':
            element = '2'
        elif label['element'] == 'search':
            element = '3'
        elif label['element'] == 'list':
            element = '4'
        return " " + str(x_min) + "," + str(y_min) + "," + str(x_max) + "," + str(y_max) + "," + element

    label_news = ""
    indices = os.listdir(label_root)
    indices = [int(i[:-4]) for i in indices]
    indices.sort(key=lambda x: x)
    for index in indices:
        if index <= start_point:
            continue
        label_path = label_root + '/' + str(index) + '.csv'
        img_path = img_root + '/' + str(index + stamp)

        label = pd.read_csv(label_path)
        label_new = {}
        for i in range(len(label)):
            l = label.iloc[i]
            seg_no = str(int(l['segment_no']))
            if seg_no not in label_new:
                label_new[seg_no] = img_path + '/' + seg_no + ".png"
            label_new[seg_no] += box_convert(l)

        if len(label_new) > 0:
            label_news += "\n".join(label_new.values())
            label_news += '\n'

    open('label.txt', 'w').write(label_news)
    open('label_colab.txt', 'w').write(label_news.replace(img_root, './data'))
    return label_news


# covert labels into YOLO and colab format
l = label_convert(stamp, start_point, label_root, img_root)
