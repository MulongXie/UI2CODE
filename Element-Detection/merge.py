import json
import cv2
import numpy as np
from os.path import join as pjoin
import os
import time
from random import randint as rint

from utils.util_merge import *
from config.CONFIG import Config
from utils.Element import Element
C = Config()


def merge_by_text(org, compos, texts):
    compos_new = []

    for compo in compos:
        # broad = draw_bounding_box(org, [a], show=True)
        new_compo = None
        text_area = 0
        for text in texts:
            # get the intersected area
            inter = compo.calc_intersection_area(text)
            if inter == 0:
                continue

            # calculate IoU
            ioa = inter / compo.area
            iob = inter / text.area
            iou = inter / (compo.area + text.area - inter)

            # print('ioa:%.3f, iob:%.3f, iou:%.3f' %(ioa, iob, iou))
            # draw_bounding_box(broad, [b], color=(255,0,0), line=2, show=True)

            # text area
            if ioa >= 0.68 or iou > 0.55:
                new_compo = compo.element_merge(text, new_element=True, new_category='Text')
                break
            text_area += inter

        # print("Text area ratio:%.3f" % (text_area / area_a))
        if new_compo is not None:
            compos_new.append(new_compo)
        elif text_area / compo.area > 0.55:
            compo.category = 'Text'
            compos_new.append(compo)
        else:
            compos_new.append(compo)

    return compos_new


def incorporate(img_path, compo_path, text_path, output_root, resize_by_height=None, show=False):
    org = cv2.imread(img_path)

    compos = []
    texts = []

    background = None
    for compo in json.load(open(compo_path, 'r'))['compos']:
        if compo['class'] == 'Background':
            background = compo
            continue
        element = Element((compo['column_min'], compo['row_min'], compo['column_max'], compo['row_max']), compo['class'])
        compos.append(element)
    for text in json.load(open(text_path, 'r'))['compos']:
        element = Element((text['column_min'], text['row_min'], text['column_max'], text['row_max']), 'Text')
        texts.append(element)

    # bbox_text = refine_text(org, bbox_text, 20, 10)
    # bbox_text = resize_label(bbox_text, resize_by_height, org.shape[0])

    org_resize = resize_img_by_height(org, resize_by_height)
    # draw_bounding_box_class(org_resize, bbox_compos, class_compos, show=show, name='ip')
    # draw_bounding_box(org_resize, bbox_text, show=show, name='ocr')

    compos_merged = merge_by_text(org_resize, compos, texts)
    draw_bounding_box(org_resize, compos_merged, show=show, name='ocr')
    compos_merged = merge_redundant_corner(compos_merged)

    board = draw_bounding_box_class(org_resize, compos_merged, name='merged', show=show)
    draw_bounding_box_non_text(org_resize, compos_merged, org_shape=org.shape, show=show)
    compos_json = save_corners_json(pjoin(output_root, 'compo.json'), background, compos_merged, org_resize.shape)
    dissemble_clip_img_fill(pjoin(output_root, 'clips'), org_resize, compos_json)
    cv2.imwrite(pjoin(output_root, 'result.jpg'), board)

    print('Merge Complete and Save to', pjoin(output_root, 'result.jpg'))
    print(time.ctime(), '\n')
    if show:
        cv2.destroyAllWindows()
