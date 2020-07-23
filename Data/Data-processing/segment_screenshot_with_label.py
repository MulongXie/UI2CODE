import segmentation as seg
import cv2
import os
import numpy as np


def segment_by_elements(elements, full_height):
    # from highest one
    mark = np.full(len(elements), False)

    cur_height = 600
    while True:
        changed = False
        while True:
            for i, element in enumerate(elements):
                if not mark[i] and element['by'] < cur_height:
                    h = element['by'] + element['bh']
                    if h > cur_height:
                        cur_height = h
                    mark[i] = True
                    changed = True
            if not changed:
                break

        if cur_height == full_height:
            break

        h = cur_height + 600
        cur_height = full_height if h > full_height else h


img = cv2.imread('data/org.png')
img_segment_dir = 'data/segment'
os.makedirs(img_segment_dir, exist_ok=True)

segment_by_elements()
