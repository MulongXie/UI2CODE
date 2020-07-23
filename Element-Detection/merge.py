import json
import cv2
import numpy as np
from os.path import join as pjoin
import os
import time
from random import randint as rint

from utils.util_merge import *
from config.CONFIG import Config
C = Config()


def merge_by_text(org, corners_compo_old, compos_class_old, corner_text):
    def merge_two_corners(corner_a, corner_b):
        (col_min_a, row_min_a, col_max_a, row_max_a) = corner_a
        (col_min_b, row_min_b, col_max_b, row_max_b) = corner_b

        col_min = min(col_min_a, col_min_b)
        col_max = max(col_max_a, col_max_b)
        row_min = min(row_min_a, row_min_b)
        row_max = max(row_max_a, row_max_b)
        return [col_min, row_min, col_max, row_max]

    corners_compo_refine = []
    compos_class_refine = []

    for i in range(len(corners_compo_old)):
        a = corners_compo_old[i]
        # broad = draw_bounding_box(org, [a], show=True)
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        new_corner = None
        text_area = 0
        for b in corner_text:
            area_b = (b[2] - b[0]) * (b[3] - b[1])
            # get the intersected area
            col_min_s = max(a[0], b[0])
            row_min_s = max(a[1], b[1])
            col_max_s = min(a[2], b[2])
            row_max_s = min(a[3], b[3])
            w = np.maximum(0, col_max_s - col_min_s)
            h = np.maximum(0, row_max_s - row_min_s)
            inter = w * h
            if inter == 0:
                continue

            # calculate IoU
            ioa = inter / area_a
            iob = inter / area_b
            iou = inter / (area_a + area_b - inter)

            # print('ioa:%.3f, iob:%.3f, iou:%.3f' %(ioa, iob, iou))
            # draw_bounding_box(broad, [b], color=(255,0,0), line=2, show=True)

            # text area
            if ioa >= 0.68 or iou > 0.6:
                new_corner = merge_two_corners(a, b)
                break
            # text_area += inter

        if new_corner is not None:
            corners_compo_refine.append(new_corner)
            compos_class_refine.append('TextView')
        elif text_area / area_a > 0.4:
            corners_compo_refine.append(corners_compo_old[i])
            compos_class_refine.append('TextView')
        else:
            corners_compo_refine.append(corners_compo_old[i])
            compos_class_refine.append(compos_class_old[i])

    return corners_compo_refine, compos_class_refine


def incorporate(img_path, compo_path, text_path, output_root, resize_by_height=None, show=False):
    name = img_path.split('/')[-1][:-4]
    org = cv2.imread(img_path)

    compos = json.load(open(compo_path, 'r'))
    texts = json.load(open(text_path, 'r'))
    bbox_compos = []
    class_compos = []
    bbox_text = []
    background = None
    for compo in compos['compos']:
        if compo['class'] == 'Background':
            background = compo
            continue
        bbox_compos.append([compo['column_min'], compo['row_min'], compo['column_max'], compo['row_max']])
        class_compos.append(compo['class'])
    for text in texts['compos']:
        bbox_text.append([text['column_min'], text['row_min'], text['column_max'], text['row_max']])

    # bbox_text = refine_text(org, bbox_text, 20, 10)
    # bbox_text = resize_label(bbox_text, resize_by_height, org.shape[0])

    org_resize = resize_img_by_height(org, resize_by_height)
    draw_bounding_box_class(org_resize, bbox_compos, class_compos, show=show, name='ip')
    draw_bounding_box(org_resize, bbox_text, show=show, name='ocr')

    corners_compo_merged, compos_class_merged = merge_by_text(org_resize, bbox_compos, class_compos, bbox_text)
    corners_compo_merged, compos_class_merged = merge_redundant_corner(corners_compo_merged, compos_class_merged)
    corners_compo_merged = refine_corner(corners_compo_merged, shrink=0)

    board = draw_bounding_box_class(org_resize, corners_compo_merged, compos_class_merged)
    draw_bounding_box_non_text(org_resize, corners_compo_merged, compos_class_merged, org_shape=org.shape, show=show)
    compos_json = save_corners_json(pjoin(output_root, 'compo.json'), background, corners_compo_merged, compos_class_merged)
    dissemble_clip_img_fill(pjoin(output_root, 'clips'), org_resize, compos_json)
    cv2.imwrite(pjoin(output_root, 'result.jpg'), board)

    if show:
        cv2.imshow('merge', board)
        cv2.waitKey()

    print('Merge Complete and Save to', pjoin(output_root, 'result.jpg'))
    print(time.ctime(), '\n')
    if show:
        cv2.destroyAllWindows()
