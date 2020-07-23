'''
convert the labels into YOLO format
'''
import os
import numpy as np
import pandas as pd
import cv2


def label_convert(label_root, img_root):

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

    stamp = 0

    label_news = ""
    indices = os.listdir(label_root)
    indices = [i[:-4] for i in indices]
    indices.sort(key=lambda x: int(x))
    for index in indices:
        label_path = label_root + '/' + index + '.csv'
        img_path = img_root + '/' + str(int(index) + stamp)

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


def draw_label_txt(line):
    colors = [(255, 0, 255), (255, 160, 0), (0, 150, 255), (255, 150, 255), (255, 255, 0)]
    ele_name = ['button', 'input', 'select', 'search', 'list']
    line = line.split()
    print(line[0])
    img = cv2.imread(line[0])
    label = line[1:]

    for i in range(len(label)):
        # col_min, row_min, col_max, row_max, element_class
        l = [int(e) for e in label[i].split(',')]
        element = ele_name[l[-1]]
        color = colors[l[-1]]
        cv2.rectangle(img, (l[0], l[1]), (l[2], l[3]), color, 1)
        cv2.putText(img, element, (l[0], l[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    cv2.imshow('img', img)
    cv2.waitKey()


img_root = 'E:\Mulong\Datasets\dataset_webpage\manually_labelled\data'
label_root = 'E:\Mulong\Datasets\dataset_webpage\manually_labelled\label'
l = label_convert(label_root, img_root)
