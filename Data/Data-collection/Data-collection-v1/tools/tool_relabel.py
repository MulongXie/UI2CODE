from glob import glob
from os.path import join as pjoin
import cv2
import os
import numpy as np
import pandas as pd

ix, iy = -1, -1
# global variables for visualisation
gb_img = None  # record the new label
gb_label = None  # label of this web page
gb_label_index = None  # index of the new line of label
gb_element = None
gb_is_labeling = False


def draw_label(label, img):
    if gb_element == 'button':
        color = (255, 0, 255)
    elif gb_element == 'input':
        color = (255, 160, 0)
    elif gb_element == 'select':
        color = (0, 150, 255)
    elif gb_element == 'search':
        color = (255, 150, 255)
    elif gb_element == 'list':
        color = (255, 255, 0)

    if not gb_is_labeling:
        color = (0, 0, 255)
    else:
        label = label[label['element'] == gb_element]
    for i in range(len(label)):
        l = label.iloc[i]
        element = l['element'] if not gb_is_labeling else gb_element
        cv2.rectangle(img, (int(l['bx']), int(l['by'])), (int(l['bx'] + l['bw']), int(l['by'] + l['bh'])), color, 1)
        cv2.putText(img, element, (int(l['bx']), int(l['by'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    cv2.imshow('img', img)


def add_label(label, ix, iy, x, y, segment_no, element):
    l = {'bx': ix, 'by': iy, 'bh': int(y - iy), 'bw': int(x - ix), 'segment_no': int(segment_no),
         'element': element}
    label = label.append(l, ignore_index=True)
    return label


def relabel(event, x, y, flags, param):
    global ix, iy, gb_img, gb_label, gb_label_index, gb_element
    seg_index = param[0]

    if event == cv2.EVENT_LBUTTONDOWN:
        # fetch the start points
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        # draw the rectangle
        img = gb_img.copy()
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 1)
        cv2.putText(img, gb_element, (ix, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.imshow('img', img)
    elif event == cv2.EVENT_LBUTTONUP:
        # save the labeled area
        gb_label_index += 1
        gb_label = add_label(gb_label, ix, iy, x, y, seg_index, gb_element)
        draw_label(gb_label, gb_img)
    elif event == cv2.EVENT_MOUSEMOVE:
        img = gb_img.copy()
        cv2.line(img, (x, y), (x + 40, y), (0, 0, 255), 1, cv2.LINE_AA)
        cv2.line(img, (x, y), (x, y + 40), (0, 0, 255), 1, cv2.LINE_AA)
        cv2.imshow('img', img)


def add_tips(flag):
    img = np.zeros((150, 400, 3), dtype=np.uint8)
    font_scale = 0.5
    color = (255, 255, 255)
    thick = 1
    # webpage-level
    if flag == 0:
        cv2.putText(img, 'a: Go Previous Image', (0, 20), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 'd: Go Next Image', (0, 40), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 's: Start Relabelling', (0, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 'q: Go Next WebPage & Discard Label', (0, 100), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 'r: Remove Labels of This Image', (0, 120), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 'n: Terminate Program', (0, 140), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
    # segment-level
    elif flag == 1:
        cv2.putText(img, 'd: Quit Relabelling Mode', (0, 20), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, 'z: Delete the Last Label', (0, 40), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)

        cv2.putText(img, '1: button', (0, 60), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, '2: input', (0, 80), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, '3: select', (0, 100), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, '4: search', (0, 120), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
        cv2.putText(img, '5: list', (0, 140), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thick)
    cv2.imshow('tips', img)
    cv2.moveWindow('tips', 2000, 0)


def view_data(start_point, data_position='E:\Mulong\Datasets\dataset_webpage\page10000'):
    # *** step 1 *** Root Path
    # retrieve global variables for relabel
    global gb_img, gb_label, gb_label_index, gb_element, gb_is_labeling
    # set root path
    img_root = pjoin(data_position, 'ip_img_segment')
    relabel_root = pjoin(data_position, 'relabel')  # relabels path
    if not os.path.exists(img_root):
        print('No such dataset')
        return 0

    # *** step 2 *** Iterate Web Pages
    # iterate all web pages from the start point
    img_dirs = glob(pjoin(img_root, '*'))
    img_dirs.sort(key=lambda x: int(x.split('\\')[-1]))
    for dir in img_dirs:
        index = dir.split('\\')[-1]
        if start_point > int(index):
            continue
        # set paths
        path_img_segs = glob(pjoin(dir, '*.png'))
        path_relabel = pjoin(relabel_root, index + '.csv')
        print("\n*** Start Checking %s ***" % (dir))

        # *** step 3 *** Iterate Segment Images
        # iterate all image segments for each web page
        save = True
        move = True
        passed = {}
        s = 0
        label = pd.read_csv(pjoin(data_position, 'format.csv'), index_col=0)
        while s < len(path_img_segs):
            # show tips
            add_tips(0)

            # read segment image
            seg_img = cv2.imread(path_img_segs[s])
            seg_index = int(path_img_segs[s].split('\\')[-1][:-4])
            if move:
                if path_img_segs[s] is not '':
                    print(path_img_segs[s])
                gb_img = seg_img.copy()
                gb_element = 'button'
                try:
                    gb_label = label[label['segment_no'] == seg_index]
                except:
                    gb_label = label.copy()
                move = False

            # *** step 4 *** Web Page-Level Options
            # draw labels on the segment image
            draw_label(gb_label, gb_img)
            key = cv2.waitKey(0)

            # back to the previous image
            if key == ord('a'):
                s = s - 1 if s >= 1 else 0
                move = True
                continue
            # next image
            elif key == ord('d'):
                s += 1
                move = True
                if str(seg_index) in passed:
                    continue
            # remove all existing labels
            elif key == ord('r'):
                gb_img = seg_img.copy()
                gb_label = gb_label.drop(index=gb_label.index.values)
                label = label.drop(index=label[label['segment_no'] == seg_index].index.values)
                print('*** Remove Labels of Image %d ***' % seg_index)
            # skip rest segment images and discard the current relabel
            elif key == ord('q'):
                s += 1
                move = True
                print('*** Image is Discarded ***')
                continue
            elif key == ord('e'):
                save = False
                print('*** Next Web Page ***\n')
                break
            # terminate the program
            elif key == ord('n'):
                print('\n*** Program Terminated ***')
                return

            # *** step 5 *** Segment-Level Options
            # enter label mode
            elif key == ord('s'):
                # show tips
                add_tips(1)

                gb_label_index = len(gb_label) - 1
                gb_is_labeling = True
                # set mouse callback function
                cv2.setMouseCallback('img', relabel, [seg_index])
                while (1):
                    print('Label for <%s>' % gb_element)
                    k = cv2.waitKey(0)
                    # withdraw the last label
                    if k == ord('z'):
                        if gb_label_index >= 0:
                            gb_label = gb_label.drop(index=gb_label.index[gb_label_index])
                            gb_label_index -= 1
                        gb_img = seg_img.copy()
                        draw_label(gb_label, gb_img)

                    # quit label mode
                    elif k == ord('d'):
                        move = True
                        gb_is_labeling = False
                        break

                    # different kinds of elements
                    elif k == ord('1'):
                        gb_element = 'button'
                    elif k == ord('2'):
                        gb_element = 'input'
                    elif k == ord('3'):
                        gb_element = 'select'
                    elif k == ord('4'):
                        gb_element = 'search'
                    elif k == ord('5'):
                        gb_element = 'list'

            else:
                continue

            cv2.destroyAllWindows()
            label = label.append(gb_label, ignore_index=True, sort=False)
            passed[str(seg_index)] = 1
            print('... Number of Current Labels: %d ...' % len(label))

        if save and len(label) > 0:
            label.to_csv(path_relabel)
            print('*** %d Labels Saved to %s ***\n' % (len(label), path_relabel))


view_data(4102)