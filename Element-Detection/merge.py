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


def reclassify_text_by_ocr(org, compos, texts):
    mark_compo = np.full(len(compos), False)
    mark_text = np.full(len(texts), False)
    compos_new = []
    for i, compo in enumerate(compos):
        # broad = draw_bounding_box(org, [compo], show=True)
        new_compo = None
        text_area = 0
        for j, text in enumerate(texts):
            # get the intersected area
            inter = compo.calc_intersection_area(text)
            if inter == 0:
                continue

            # calculate IoU
            ioa = inter / compo.area
            iob = inter / text.area
            iou = inter / (compo.area + text.area - inter)

            # print('ioa:%.3f, iob:%.3f, iou:%.3f' %(ioa, iob, iou))
            # draw_bounding_box(broad, [text], color=(255,0,0), line=2, show=True)

            # text area
            if ioa >= 0.68 or iou > 0.55:
                if mark_text[j]:
                    mark_compo[i] = True
                else:
                    new_compo = compo.element_merge(text, new_element=True, new_category='Text')
                    mark_text[j] = True
                break
            text_area += inter

        # print("Text area ratio:%.3f" % (text_area / compo.area))
        if new_compo is not None:
            compos_new.append(new_compo)
        elif text_area / compo.area > 0.5:
            compo.category = 'Text'
            compos_new.append(compo)
        elif not mark_compo[i]:
            compos_new.append(compo)
    return compos_new


def merge_redundant_corner(org, compos):
    changed = False
    new_compos = []
    for i in range(len(compos)):
        # broad = draw_bounding_box(org, [compos[i]], show=True)
        merged = False
        for j in range(len(new_compos)):
            iou = compos[i].calc_iou(new_compos[j])

            # if iou > 0:
            #     print('iou:%.3f' % iou)
            #     draw_bounding_box(broad, [new_compos[j]], color=(255,0,0), line=2, show=True)

            if iou > 0.8:
                new_compos[j].element_merge(compos[i], new_element=False)
                merged = True
                changed = True
                break
        if not merged:
            new_compos.append(compos[i])

    if not changed:
        return compos
    else:
        return merge_redundant_corner(org, new_compos)


def merge_intersected_compos(compos):
    changed = False
    new_compos = []
    for i in range(len(compos)):
        merged = False
        for j in range(len(new_compos)):
            relation = compos[i].element_relation(new_compos[j])
            if relation == 2 or relation == -1:
                # draw.draw_bounding_box(org, [compos[i], new_compos[j]], name='b-merge', show=True)
                new_compos[j].element_merge(compos[i])
                # draw.draw_bounding_box(org, [new_compos[j]], name='a-merge', show=True)
                merged = True
                changed = True
                break
        if not merged:
            new_compos.append(compos[i])

    if not changed:
        return compos
    else:
        return merge_intersected_compos(new_compos)


def merge_text_line(compos, max_word_gap=4, max_word_height=20):
    changed = False
    new_compos = []
    for i in range(len(compos)):
        if compos[i].category != 'Text':
            new_compos.append(compos[i])
            continue
        merged = False
        height = compos[i].height
        if height > max_word_height:
            new_compos.append(compos[i])
            continue
        for j in range(len(new_compos)):
            # merge text line and paragraph
            if is_same_alignment(compos[i], new_compos[j], max_word_gap, flag='line'):
                new_compos[j].element_merge(compos[i])
                new_compos[j].category = 'Text'
                merged = True
                changed = True
                break
        if not merged:
            new_compos.append(compos[i])

    if not changed:
        return compos
    else:
        return merge_text_line(new_compos)


def merge_paragraph(compos, max_para_gap=8, max_word_height=20):
    changed = False
    new_compos = []
    for i in range(len(compos)):
        if compos[i].category != 'Text':
            new_compos.append(compos[i])
            continue
        merged = False
        height = compos[i].height
        if height > max_word_height:
            new_compos.append(compos[i])
            continue
        for j in range(len(new_compos)):
            if is_same_alignment(compos[i], new_compos[j], max_para_gap, flag='paragraph'):
                if new_compos[j].category != 'Text':
                    continue
                new_compos[j].element_merge(compos[i])
                merged = True
                changed = True
                break
        if not merged:
            new_compos.append(compos[i])

    if not changed:
        return compos
    else:
        return merge_paragraph(new_compos)


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
    draw_bounding_box_class(org_resize, compos, show=show, name='ip')
    draw_bounding_box(org_resize, texts, show=show, name='ocr')

    compos_merged = reclassify_text_by_ocr(org_resize, compos, texts)
    compos_merged = merge_redundant_corner(org_resize, compos_merged)
    draw_bounding_box_class(org_resize, compos_merged, name='text', show=show)

    compos_merged = merge_text_line(compos_merged)
    draw_bounding_box_class(org_resize, compos_merged, name='merged line', show=show)
    compos_merged = merge_paragraph(compos_merged)
    draw_bounding_box_class(org_resize, compos_merged, name='merged paragraph', show=show)

    compos_merged = merge_intersected_compos(compos_merged)
    board = draw_bounding_box_class(org_resize, compos_merged, name='merged intersected', show=show)

    draw_bounding_box_non_text(org_resize, compos_merged, org_shape=org.shape, show=show)
    compos_json = save_corners_json(pjoin(output_root, 'compo.json'), background, compos_merged, org_resize.shape)
    dissemble_clip_img_fill(pjoin(output_root, 'clips'), org_resize, compos_json)
    cv2.imwrite(pjoin(output_root, 'result.jpg'), board)

    print('Merge Complete and Save to', pjoin(output_root, 'result.jpg'))
    print(time.ctime(), '\n')
    if show:
        cv2.destroyAllWindows()
