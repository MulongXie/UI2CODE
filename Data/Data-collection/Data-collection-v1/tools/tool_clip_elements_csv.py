from os.path import join as pjoin
import glob
import pandas as pd
import cv2
import numpy as np

element_map = {'0':'button', '1':'input', '2':'select', '3':'search', '4':'list'}
element_number = {'button':0, 'input':0, 'select':0, 'search':0, 'list':0, 'img':0}
ROOT_OUTPUT = "E:/Mulong/Datasets/dataset_webpage/elements"
ROOT_IMG = 'E:\Mulong\Datasets\dataset_webpage\page10000\org'
ROOT_LABEL = 'E:\Mulong\Datasets\dataset_webpage\page10000\ip_label_rec'


def clipping(img, element, x_min, y_min, x_max, y_max, output_root=ROOT_OUTPUT, pad=False, show_clip=False, write_clip=True):
    def padding():
        height = np.shape(clip)[0]
        width = np.shape(clip)[1]

        pad_height = int(height / 10)
        pad_wid = int(width / 10)
        pad_img = np.full(((height + pad_height), (width + pad_wid), 3), 255, dtype=np.uint8)
        pad_img[int(pad_height / 2):(int(pad_height / 2) + height), int(pad_wid / 2):(int(pad_wid / 2) + width)] = clip
        return pad_img

    clip = img[x_min:x_max, y_min:y_max]
    if pad:
        clip = padding()
    if write_clip:
        cv2.imwrite(pjoin(output_root, element, str(element_number[element]) + '.png'), clip)
    if show_clip:
        cv2.imshow('clip', clip)
        cv2.waitKey(0)


def fetch_and_clip_csv(img, label, show=False):
    # 'x_min, y_min, x_max, y_max, element'
    for i in range(len(label)):

        ele = label.iloc[i]
        if ele['component'] != 'img' or int(ele['height']) > 800 or int(ele['width']) > 1200:
            continue

        x_min = int(ele['x_min'])
        y_min = int(ele['y_min'])
        x_max = int(ele['x_max'])
        y_max = int(ele['y_max'])
        element = 'img'
        element_number[element] += 1

        clipping(img, element, x_min, y_min, x_max, y_max)

        if show:
            cv2.rectangle(img, (y_min, x_min), (y_max, x_max), (0, 0, 255), 1)
            cv2.imshow('img', img)
            cv2.waitKey(0)


def read_labels_csv():
    label_paths = glob.glob(pjoin(ROOT_LABEL, '*csv'))
    label_paths.sort(key=lambda x: int(x.split('\\')[-1][:-4]))

    for label_path in label_paths:
        index = label_path.split('\\')[-1][:-4]
        img_path = pjoin(ROOT_IMG, index + '.png')
        print(img_path)

        img = cv2.imread(img_path)
        label = pd.read_csv(label_path)

        fetch_and_clip_csv(img, label)

    print(element_number)


read_labels_csv()
