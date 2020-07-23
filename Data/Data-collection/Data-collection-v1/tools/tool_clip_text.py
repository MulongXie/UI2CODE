import pytesseract as pyt
import cv2
import numpy as np
import glob
from os.path import join as pjoin

ROOT_CLEAN_IMG = 'E:\Mulong\Datasets\dataset_webpage\page10000\ip_img_clean'
ROOT_OUTPUT = "E:/Mulong/Datasets/dataset_webpage/elements/text"


def clipping(img, corners, output_root=ROOT_OUTPUT, pad=False, show_clip=False, write_clip=True):
    def padding():
        height = np.shape(clip)[0]
        width = np.shape(clip)[1]

        pad_height = int(height / 10)
        pad_wid = int(width / 10)
        pad_img = np.full(((height + pad_height), (width + pad_wid), 3), 255, dtype=np.uint8)
        pad_img[int(pad_height / 2):(int(pad_height / 2) + height), int(pad_wid / 2):(int(pad_wid / 2) + width)] = clip
        return pad_img

    for i, corner in enumerate(corners):
        (top_left, bottom_right) = corner
        (col_min, row_min) = top_left
        (col_max, row_max) = bottom_right

        clip = img[row_min:row_max, col_min:col_max]
        if pad:
            clip = padding()
        if write_clip:
            cv2.imwrite(pjoin(output_root, str(i) + '.png'), clip)
        if show_clip:
            cv2.imshow('clip', clip)
            cv2.waitKey(0)


def text_detection(img_clean, show=False):
    try:
        data = pyt.image_to_data(img_clean).split('\n')
        broad = img_clean.copy()
    except:
        return None
    corners_word = []
    for d in data[1:]:
        d = d.split()
        if d[-1] != '-1':
            if d[-1] != '-' and d[-1] != '—' and 5 < int(d[-3]) < 40 and 5 < int(d[-4]) < 100:
                t_l = (int(d[-6]), int(d[-5]))
                b_r = (int(d[-6]) + int(d[-4]), int(d[-5]) + int(d[-3]))
                corners_word.append((t_l, b_r))
                cv2.rectangle(broad, t_l, b_r, (0, 0, 255), 1)

    if show:
        cv2.imshow('a', broad)
        cv2.waitKey()
    return corners_word


def read_img():

    img_paths = glob.glob(pjoin(ROOT_CLEAN_IMG, '*.png'))
    img_paths.sort(key=lambda x: int(x.split('\\')[-1][:-4]))

    start_index = 5647
    end_index = 20000

    for img_path in img_paths:
        index = img_path.split('\\')[-1][:-4]
        if int(index) < start_index:
            continue
        if int(index) > end_index:
            break

        print(img_path)

        img = cv2.imread(img_path)
        corners_word = text_detection(img)
        if corners_word is not None:
            clipping(img, corners_word)


read_img()
