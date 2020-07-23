import pandas as pd
import cv2
import numpy as np
import os


def select_color(item):
    color = (0, 0, 0)
    if item == 'div':
        color = (0, 0, 200)
    elif item == 'input':
        color = (255, 0, 0)
    elif item == 'button':
        color = (180, 0, 0)
    elif item == 'h1':
        color = (0, 255, 0)
    elif item == 'h2':
        color = (0, 180, 0)
    elif item == 'p':
        color = (0, 100, 0)
    elif item == 'a':
        color = (200, 100, )
    elif item == 'img':
        color = (0, 100, 255)
    return color


def draw(label, pic):
    count = {}
    for i in range(0, len(label)):
        item = label.iloc[i]

        top_left = (int(item.bx), int(item.by))
        botom_right = (int(item.bx + item.bw), int(item.by + item.bh))
        element = item.element

        color = select_color(item.element)
        if element in count:
            count[element] += 1
        else:
            count[element] = 1

        pic = cv2.rectangle(pic, top_left, botom_right, color, 1)
        cv2.putText(pic, element + str(count[element]), top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)


def label(label, img, output_path, show=False):
    if np.shape(img) == ():
        return
    img = cv2.resize(img, (int(np.shape(img)[1]), int(np.shape(img)[0])))
    draw(label, img)

    if show:
        cv2.imshow('img', img)
        cv2.waitKey(0)

    cv2.imwrite(output_path, img)


# used for sorting by area
def takearea(element):
    return element['area']


def wireframe(label, image, output_path):
    pic = np.zeros(np.shape(image), np.uint8)
    pic.fill(255)

    layers = []
    for i in range(0, len(label)):
        item = label.iloc[i]
        element = item.element
        if element == 'div':
            continue

        layer = {}
        layer['top_left'] = (int(item.bx), int(item.by))
        layer['bottom_right'] = (int(item.bx + item.bw), int(item.by + item.bh))
        layer['area'] = int(item.bw * item.bh)
        layer['color'] = select_color(element)
        layer['element'] = element
        layers.append(layer)

    # sort in descent order
    layers.sort(key=takearea, reverse=True)

    count = {}  # count for each component category
    for l in layers:
        element = l['element']
        if element in count:
            count[element] += 1
        else:
            count[element] = 1

        pic = cv2.rectangle(pic, l['top_left'], l['bottom_right'], l['color'], -1)
        cv2.putText(pic, element + str(count[element]), l['top_left'], cv2.FONT_HERSHEY_SIMPLEX, 0.5, l['color'], 2,
                    cv2.LINE_AA)

    cv2.imwrite(output_path, pic)
    print(output_path)


# avoid blank component
def compo_scan(org_img_path, label_path):
    # read img and its label
    img = cv2.imread(org_img_path)
    label = pd.read_csv(label_path, index_col=0)

    label_scanned = pd.DataFrame(columns=label.columns.values)

    index = 0
    for i in range(len(label)):
        compo = label.iloc[i]
        # get the clip img of that component
        clip = img[compo['by']:compo['by'] + compo['bh'], compo['bx']:compo['bx'] + compo['bw'], :]
        # calculate the average pixel value and discard blank ones that are pure withe
        avg_pix = clip.sum() / (clip.shape[0] * clip.shape[1] * clip.shape[2])
        if avg_pix < 245:
            label_scanned.loc[index] = compo
            index += 1

    label_scanned.to_csv(label_path)