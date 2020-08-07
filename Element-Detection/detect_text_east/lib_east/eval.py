import cv2
import time
import math
import os
import numpy as np
import tensorflow as tf
import json

import detect_text_east.lib_east.locality_aware_nms as nms_locality
import detect_text_east.lib_east.lanms as lanms
import detect_text_east.lib_east.model as model
from detect_text_east.lib_east.icdar import restore_rectangle

from config.CONFIG import Config
cfg = Config()


def resize_label(bboxes, gt_height, d_height, bias=0):
    bboxes_new = []
    scale = gt_height/d_height
    for bbox in bboxes:
        bbox = [int(b * scale + bias) for b in bbox]
        bboxes_new.append(bbox)
    return bboxes_new


def save_corners_json(file_path, corners, new=True):
    if not new:
        f_in = open(file_path, 'r')
        components = json.load(f_in)
    else:
        components = {'compos': []}

    for i in range(len(corners)):
        c = {}
        (c['column_min'], c['row_min'], c['column_max'], c['row_max']) = corners[i]
        components['compos'].append(c)
    json.dump(components,  open(file_path, 'w'), indent=4)


def draw_bounding_box(org, corners, color=(0, 0, 255), line=2, show=False, name='image'):
    board = org.copy()
    for i in range(len(corners)):
        board = cv2.rectangle(board, (corners[i][0], corners[i][1]), (corners[i][2], corners[i][3]), color, line)
    if show:
        # cv2.imshow(name, cv2.resize(board, (500, 800)))
        cv2.imshow(name, board)
        cv2.waitKey(0)
    return board


def merge_text(corners, max_word_gad=10):
    def is_text_line(corner_a, corner_b):
        (col_min_a, row_min_a, col_max_a, row_max_a) = corner_a
        (col_min_b, row_min_b, col_max_b, row_max_b) = corner_b

        col_min_s = max(col_min_a, col_min_b)
        row_min_s = max(row_min_a, row_min_b)
        col_max_s = min(col_max_a, col_max_b)
        row_max_s = min(row_max_a, row_max_b)
        w = np.maximum(0, col_max_s - col_min_s)
        h = np.maximum(0, row_max_s - row_min_s)
        inter = w * h
        area_a = (col_max_a - col_min_a) * (row_max_a - row_min_a)
        area_b = (col_max_b - col_min_b) * (row_max_b - row_min_b)
        iou = inter / (area_a + area_b - inter)

        # on the same line
        if abs(row_min_a - row_min_b) < max_word_gad and abs(row_max_a - row_max_b) < max_word_gad:
            # close distance
            if abs(col_min_b - col_max_a) < max_word_gad or abs(col_min_a - col_max_b) < max_word_gad:
                return True
            # intersected
            if iou > 0.1:
                return True
        return False

    def corner_merge_two_corners(corner_a, corner_b):
        (col_min_a, row_min_a, col_max_a, row_max_a) = corner_a
        (col_min_b, row_min_b, col_max_b, row_max_b) = corner_b

        col_min = min(col_min_a, col_min_b)
        col_max = max(col_max_a, col_max_b)
        row_min = min(row_min_a, row_min_b)
        row_max = max(row_max_a, row_max_b)
        return col_min, row_min, col_max, row_max

    changed = False
    new_corners = []
    for i in range(len(corners)):
        merged = False
        for j in range(len(new_corners)):
            if is_text_line(corners[i], new_corners[j]):
                new_corners[j] = corner_merge_two_corners(corners[i], new_corners[j])
                merged = True
                changed = True
                break
        if not merged:
            new_corners.append(corners[i])

    if not changed:
        return corners
    else:
        return merge_text(new_corners)


class FLAG:
    def __init__(self, input_img_path=None, output_label_path=None):
        self.test_data_path = input_img_path
        self.gpu_list = '0'
        self.checkpoint_path = cfg.EAST_PATH
        self.output_dir = output_label_path
        self.no_write_images = True

    def renew_path(self, input_img_path, output_label_path):
        self.test_data_path = input_img_path
        self.output_dir = output_label_path


FLAGS = FLAG()


def get_images():
    '''
    find image files in test data path
    :return: list of files found
    '''
    files = []
    exts = ['jpg', 'png', 'jpeg', 'JPG']
    for parent, dirnames, filenames in os.walk(FLAGS.test_data_path):
        for filename in filenames:
            for ext in exts:
                if filename.endswith(ext):
                    files.append(os.path.join(parent, filename))
                    break
    # print('Find {} images'.format(len(files)))
    return files


def resize_image(im, max_side_len=2400):
    '''
    resize image to a size multiple of 32 which is required by the network
    :param im: the resized image
    :param max_side_len: limit of max image size to avoid out of memory in gpu
    :return: the resized image and the resize ratio
    '''
    h, w, _ = im.shape

    resize_w = w
    resize_h = h

    # limit the max side
    if max(resize_h, resize_w) > max_side_len:
        ratio = float(max_side_len) / resize_h if resize_h > resize_w else float(max_side_len) / resize_w
    else:
        ratio = 1.
    resize_h = int(resize_h * ratio)
    resize_w = int(resize_w * ratio)

    resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 - 1) * 32
    resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 - 1) * 32
    resize_h = max(32, resize_h)
    resize_w = max(32, resize_w)
    im = cv2.resize(im, (int(resize_w), int(resize_h)))

    ratio_h = resize_h / float(h)
    ratio_w = resize_w / float(w)

    return im, (ratio_h, ratio_w)


def detect(score_map, geo_map, timer, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):
    '''
    restore text boxes from score map and geo map
    :param score_map:
    :param geo_map:
    :param timer:
    :param score_map_thresh: threshhold for score map
    :param box_thresh: threshhold for boxes
    :param nms_thres: threshold for nms
    :return:
    '''
    if len(score_map.shape) == 4:
        score_map = score_map[0, :, :, 0]
        geo_map = geo_map[0, :, :, ]
    # filter the score map
    xy_text = np.argwhere(score_map > score_map_thresh)
    # sort the text boxes via the y axis
    xy_text = xy_text[np.argsort(xy_text[:, 0])]
    # restore
    start = time.time()
    text_box_restored = restore_rectangle(xy_text[:, ::-1] * 4, geo_map[xy_text[:, 0], xy_text[:, 1], :])  # N*4*2
    # print('{} text boxes before nms'.format(text_box_restored.shape[0]))
    boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)
    boxes[:, :8] = text_box_restored.reshape((-1, 8))
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]
    timer['restore'] = time.time() - start
    # nms part
    start = time.time()
    # boxes = nms_locality.nms_locality(boxes.astype(np.float64), nms_thres)
    boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thres)
    timer['nms'] = time.time() - start

    if boxes.shape[0] == 0:
        return None, timer

    # here we filter some low score boxes by the average score map, this is different from the orginal paper
    for i, box in enumerate(boxes):
        mask = np.zeros_like(score_map, dtype=np.uint8)
        cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)
        boxes[i, 8] = cv2.mean(score_map, mask)[0]
    boxes = boxes[boxes[:, 8] > box_thresh]

    return boxes, timer


def sort_poly(p):
    min_axis = np.argmin(np.sum(p, axis=1))
    p = p[[min_axis, (min_axis + 1) % 4, (min_axis + 2) % 4, (min_axis + 3) % 4]]
    if abs(p[0, 0] - p[1, 0]) > abs(p[0, 1] - p[1, 1]):
        return p
    else:
        return p[[0, 3, 2, 1]]


def predict(sess, f_score, f_geometry, input_images, resize_by_height, show=False):
    img_path = FLAGS.test_data_path
    # print(img_path)
    # im = cv2.imread(img_path)[:, :, ::-1]

    # import lib_ip.ip_preprocessing as pre
    # im, _ = pre.read_img(img_path, resize_by_height)
    im = cv2.imread(img_path)
    im = im[:, :, ::-1]

    start_time = time.time()
    im_resized, (ratio_h, ratio_w) = resize_image(im)

    timer = {'net': 0, 'restore': 0, 'nms': 0}
    start = time.time()
    score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized]})
    timer['net'] = time.time() - start

    boxes, timer = detect(score_map=score, geo_map=geometry, timer=timer)
    # print('{} : net {:.0f}ms, restore {:.0f}ms, nms {:.0f}ms'.format(
    #     img_path, timer['net']*1000, timer['restore']*1000, timer['nms']*1000))

    if boxes is not None:
        boxes = boxes[:, :8].reshape((-1, 4, 2))
        boxes[:, :, 0] /= ratio_w
        boxes[:, :, 1] /= ratio_h

    duration = time.time() - start_time
    # print('[timing] {:.3f}'.format(duration))

    # save to file
    res_file = os.path.join(
        FLAGS.output_dir,
        '{}.json'.format(
            os.path.basename(img_path).split('.')[0]))

    corners = []
    for box in boxes:
        # to avoid submitting errors
        box = sort_poly(box.astype(np.int32))
        if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3] - box[0]) < 5:
            continue
        corners.append([int(box[0, 0]), int(box[0, 1]), int(box[2, 0]), int(box[2, 1])])
        # cv2.polylines(im[:, :, ::-1], [box.astype(np.int32).reshape((-1, 1, 2))], True, color=(255, 255, 0), thickness=1)
        # cv2.rectangle(im[:, :, ::-1], (box[0][0], box[0][1]), (box[2][0], box[2][1]), (0, 0, 255), 3)

    if resize_by_height is not None:
        corners = resize_label(corners, resize_by_height, im.shape[0])
        im = cv2.resize(im, (int(resize_by_height / im.shape[0] * im.shape[1]), resize_by_height))

    # broad = draw_bounding_box(im[:, :, ::-1], corners, name='before', show=show)
    corners = merge_text(corners)
    broad = draw_bounding_box(im[:, :, ::-1], corners, name='result', show=show)
    save_corners_json(res_file, corners)

    if not FLAGS.no_write_images:
        img_path = os.path.join(FLAGS.output_dir, os.path.basename(img_path)[:-4] + '.png')
        cv2.imwrite(img_path, broad)
        cv2.imwrite(os.path.join(FLAGS.output_dir, 'result.jpg'), broad)


def load():
    import os
    os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu_list

    with tf.get_default_graph().as_default():
        input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_images')
        try:
            global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)
        except ValueError:
            tf.get_variable_scope().reuse_variables()
            global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

        f_score, f_geometry = model.model(input_images, is_training=False)

        variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
        saver = tf.train.Saver(variable_averages.variables_to_restore())

        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
        ckpt_state = tf.train.get_checkpoint_state(FLAGS.checkpoint_path)
        model_path = os.path.join(FLAGS.checkpoint_path, os.path.basename(ckpt_state.model_checkpoint_path))
        # print('Restore from {}'.format(model_path))
        saver.restore(sess, model_path)

    return sess, f_score, f_geometry, input_images


def run(input_img_path, output_label_path, resize_by_height,
        sess, f_score, f_geometry, input_images, show=False, write_img=False):
    # tf.app.flags.DEFINE_string('test_data_path', input_img_path, '')
    # tf.app.flags.DEFINE_string('gpu_list', '0', '')
    # tf.app.flags.DEFINE_string('checkpoint_path', 'E:/Mulong/Model/East/east_icdar2015_resnet_v1_50_rbox', '')
    # tf.app.flags.DEFINE_string('output_dir', output_label_path, '')
    # tf.app.flags.DEFINE_bool('no_write_images', False, 'do not write images')
    # tf.app.run(main)

    FLAGS.renew_path(input_img_path, output_label_path)
    FLAGS.no_write_images = not write_img
    predict(sess, f_score, f_geometry, input_images, resize_by_height, show=show)