import json
import cv2
import numpy as np
from os.path import join as pjoin
import os
import time
from random import randint as rint
import shutil

import detect_compo.lib_ip.ip_preprocessing as pre
import detect_compo.lib_ip.file_utils as file
import detect_compo.lib_ip.ip_detection as det
from config.CONFIG import Config
C = Config()


def draw_bounding_box_class(org, compos, color_map=C.COLOR, line=1, show=False, name='img'):
    board = org.copy()

    class_colors = {}
    for compo in compos:
        if compo.category not in class_colors:
            class_colors[compo.category] = (rint(0,255), rint(0,255), rint(0,255))

        corner = compo.put_bbox()
        board = cv2.rectangle(board, (corner[0], corner[1]), (corner[2], corner[3]), class_colors[compo.category], line)
        # board = cv2.putText(board, compo_class[i], (corners[i][0]+5, corners[i][1]+20),
        #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, class_colors[compo_class[i]], 2)
    if show:
        cv2.imshow(name, board)
        cv2.waitKey(0)
    return board


def draw_bounding_box(org, compos,  color=(0, 255, 0), line=1, show=False, name='board'):
    board = org.copy()
    for compo in compos:
        corner = compo.put_bbox()
        board = cv2.rectangle(board, (corner[0], corner[1]), (corner[2], corner[3]), color, line)
    if show:
        cv2.imshow(name, board)
        cv2.waitKey(0)
    return board


def draw_bounding_box_non_text(org, compos, org_shape=None, color=(0, 255, 0), line=1, show=False, name='non-text'):
    board = org.copy()
    for compo in compos:
        if compo.category != 'Text' or compo.width / org_shape[1] > 0.9:
            corner = compo.put_bbox()
            board = cv2.rectangle(board, (corner[0], corner[1]), (corner[2], corner[3]), color, line)
    if show:
        board_org_size = cv2.resize(board, (org_shape[1], org_shape[0]))
        # board_org_size = board_org_size[100:-110]
        cv2.imshow(name, cv2.resize(board_org_size, (board.shape[1], board.shape[0])))
        cv2.waitKey(0)
    return board


def save_corners_json(file_path, background, compos, img_shape):
    components = {'compos': [], 'img': {'shape': img_shape}}
    if background is not None: components['compos'].append(background)

    for i, compo in enumerate(compos):
        corner = compo.put_bbox()
        c = {'id':i, 'class': compo.category,
             'height': corner[3] - corner[1], 'width': corner[2] - corner[0],
             'column_min': corner[0], 'row_min': corner[1], 'column_max': corner[2], 'row_max': corner[3]}
        components['compos'].append(c)

    json.dump(components, open(file_path, 'w'), indent=4)
    return components['compos']


def resize_label(bboxes, target_height, org_height, bias=0):
    bboxes_new = []
    scale = target_height/org_height
    for bbox in bboxes:
        bbox = [int(b * scale + bias) for b in bbox]
        bboxes_new.append(bbox)
    return bboxes_new


def resize_img_by_height(org, resize_height):
    if resize_height is None:
        return org
    w_h_ratio = org.shape[1] / org.shape[0]
    resize_w = resize_height * w_h_ratio
    rezs = cv2.resize(org, (int(resize_w), int(resize_height)))
    return rezs


def refine_text(org, corners_text, max_line_gap, min_word_length):
    def refine(bin):
        head = 0
        rear = 0
        gap = 0
        get_word = False
        for i in range(bin.shape[1]):
            # find head
            if not get_word and np.sum(bin[:, i]) != 0:
                head = i
                rear = i
                get_word = True
                continue
            if get_word and np.sum(bin[:, i]) != 0:
                rear = i
                continue
            if get_word and np.sum(bin[:, i]) == 0:
                gap += 1
            if gap > max_line_gap:
                if (rear - head) > min_word_length:
                    corners_text_refine.append((head + col_min, row_min, rear + col_min, row_max))
                gap = 0
                get_word = False

        if get_word and (rear - head) > min_word_length:
            corners_text_refine.append((head + col_min, row_min, rear + col_min, row_max))

    corners_text_refine = []
    pad = 1
    for corner in corners_text:
        (col_min, row_min, col_max, row_max) = corner
        col_min = max(col_min - pad, 0)
        col_max = min(col_max + pad, org.shape[1])
        row_min = max(row_min - pad, 0)
        row_max = min(row_max + pad, org.shape[0])

        if row_max <= row_min or col_max <= col_min:
            continue

        clip = org[row_min:row_max, col_min:col_max]
        clip_bin = pre.binarization(clip)
        refine(clip_bin)
    return corners_text_refine


def merge_redundant_corner(compos):
    changed = False
    new_compos = []
    for i in range(len(compos)):
        merged = False
        for j in range(len(new_compos)):
            if compos[i].calc_iou(new_compos[j]) > 0.8:
                new_compos[j].element_merge(compos[i], new_element=False)
                merged = True
                changed = True
                break
        if not merged:
            new_compos.append(compos[i])

    if not changed:
        return compos
    else:
        return merge_redundant_corner(new_compos)


def dissemble_clip_img_fill(clip_root, org, compos, flag='most'):

    def average_pix_around(pad=6, offset=3):
        up = row_min - pad if row_min - pad >= 0 else 0
        left = col_min - pad if col_min - pad >= 0 else 0
        bottom = row_max + pad if row_max + pad < org.shape[0] - 1 else org.shape[0] - 1
        right = col_max + pad if col_max + pad < org.shape[1] - 1 else org.shape[1] - 1

        average = []
        for i in range(3):
            avg_up = np.average(org[up:row_min - offset, left:right, i])
            avg_bot = np.average(org[row_max + offset:bottom, left:right, i])
            avg_left = np.average(org[up:bottom, left:col_min - offset, i])
            avg_right = np.average(org[up:bottom, col_max + offset:right, i])
            average.append(int((avg_up + avg_bot + avg_left + avg_right)/4))
        return average

    def most_pix_around(pad=6, offset=2):
        up = row_min - pad if row_min - pad >= 0 else 0
        left = col_min - pad if col_min - pad >= 0 else 0
        bottom = row_max + pad if row_max + pad < org.shape[0] - 1 else org.shape[0] - 1
        right = col_max + pad if col_max + pad < org.shape[1] - 1 else org.shape[1] - 1

        most = []
        for i in range(3):
            val = np.concatenate((org[up:row_min - offset, left:right, i].flatten(),
                            org[row_max + offset:bottom, left:right, i].flatten(),
                            org[up:bottom, left:col_min - offset, i].flatten(),
                            org[up:bottom, col_max + offset:right, i].flatten()))
            # print(val)
            # print(np.argmax(np.bincount(val)))
            most.append(int(np.argmax(np.bincount(val))))
        return most

    if os.path.exists(clip_root):
        shutil.rmtree(clip_root)
    os.mkdir(clip_root)
    cls_dirs = []

    bkg = org.copy()
    for compo in compos:
        cls = compo['class']
        c_root = pjoin(clip_root, cls)
        c_path = pjoin(c_root, str(compo['id']) + '.jpg')
        if cls not in cls_dirs:
            os.mkdir(c_root)
            cls_dirs.append(cls)

        col_min, row_min, col_max, row_max = compo['column_min'], compo['row_min'], compo['column_max'], compo['row_max']
        clip = org[row_min:row_max, col_min:col_max]
        cv2.imwrite(c_path, clip)

        # Fill up the background area
        if flag == 'average':
            color = average_pix_around()
        elif flag == 'most':
            color = most_pix_around()
        cv2.rectangle(bkg, (col_min, row_min), (col_max, row_max), color, -1)

    cv2.imwrite(os.path.join(clip_root, 'bkg.png'), bkg)