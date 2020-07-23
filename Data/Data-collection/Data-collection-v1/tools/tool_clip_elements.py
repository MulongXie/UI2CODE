from os.path import join as pjoin
import glob
import pandas as pd
import cv2
import numpy as np

element_map = {'0':'button', '1':'input', '2':'select', '3':'search', '4':'list'}
element_number = {'button':0, 'input':0, 'select':0, 'search':0, 'list':0}
ROOT_OUTPUT = "E:/Mulong/Datasets/dataset_webpage/elements"
ROOT_IMG = 'E:/Mulong/GoogleDrive/research/code/keras-yolo3_new/'
ROOT_LABEL = 'E:/Mulong/GoogleDrive/research/code/keras-yolo3_new/label_colab.txt'


def fetch_and_clip(img, label, output_root, pad=False, show_label=False, show_clip=False, write_clip=True):

    def padding(clip):
        height = np.shape(clip)[0]
        width = np.shape(clip)[1]

        pad_height = int(height / 10)
        pad_wid = int(width / 10)
        pad_img = np.full(((height + pad_height), (width + pad_wid), 3), 255, dtype=np.uint8)
        pad_img[int(pad_height / 2):(int(pad_height / 2) + height), int(pad_wid / 2):(int(pad_wid / 2) + width)] = clip
        return pad_img

    def clipping():
        clip = img[y_min:y_max, x_min:x_max]
        if pad:
            clip = padding(clip)
        if write_clip:
            cv2.imwrite(pjoin(output_root, element, str(element_number[element]) + '.png'), clip)
        if show_clip:
            cv2.imshow('clip', clip)
            cv2.waitKey(0)

    # 'x_min, y_min, x_max, y_max, element'
    for l in label:
        l = l.split(',')
        x_min = int(l[0])
        y_min = int(l[1])
        x_max = int(l[2])
        y_max = int(l[3])
        element = element_map[l[4]]
        element_number[element] += 1

        clipping()

        if show_label:
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 1)
            cv2.imshow('img', img)
            cv2.waitKey(0)


def read_files():
    labels = open(ROOT_LABEL, 'r')
    for l in labels.readlines():
        l = l.replace('./', ROOT_IMG).split()
        img_path = l[0]
        label = l[1:]
        img = cv2.imread(img_path)

        print(img_path)

        fetch_and_clip(img, label, ROOT_OUTPUT)


read_files()
