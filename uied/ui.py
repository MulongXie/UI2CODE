import lib_uied.ip_preprocessing as pre
import lib_uied.ip_draw as draw
import lib_uied.ip_detection as det
import lib_uied.ip_segment as seg
import lib_uied.file_utils as file
import lib_uied.ocr_classify_text as ocr
from CONFIG_UIED import Config

import cv2

# initialization
C = Config()
from lib_uied.MODEL_CNN import CNN
clf = CNN()
clf.load()

is_ocr = False
is_shrink_img = False


def pre_processing(input_path, img_section):
    # *** Step 1 *** pre-processing: gray, gradient, binary
    org, gray = pre.read_img(input_path, img_section)  # cut out partial img
    binary = pre.preprocess(gray)
    return org, binary


def processing(org, binary, clf, main=True):
    if main:
        # *** Step 2 *** object detection: get connected areas -> get boundary -> get corners
        boundary_rec, boundary_non_rec = det.boundary_detection(binary, write_boundary=True)
        corners_rec = det.get_corner(boundary_rec)
        corners_non_rec = det.get_corner(boundary_non_rec)

        # *** Step 3 *** data processing: identify blocks and compos from rectangles -> identify irregular compos
        corners_block, corners_img, corners_compo = det.block_or_compo(org, binary, corners_rec)
        det.compo_irregular(org, corners_non_rec, corners_img, corners_compo)

        # *** Step 4 *** classification: clip and classify the components candidates -> ignore noises -> refine img
        compos = seg.clipping(org, corners_compo)
        compos_class = clf.predict(compos)
        corners_compo, compos_class = det.strip_img(corners_compo, compos_class, corners_img)

        # *** Step 5 *** result refinement
        if is_shrink_img:
            corners_img = det.img_shrink(org, binary, corners_img)

        # *** Step 6 *** recursive inspection: search components nested in components
        corners_block, corners_img, corners_compo, compos_class = det.compo_in_img(processing, org, binary, clf, corners_img, corners_block, corners_compo, compos_class)

        # *** Step 7 *** ocr check and text detection from cleaned image
        if is_ocr:
            corners_block, _ = det.rm_text(org, corners_block, ['block' for i in range(len(corners_block))])
            corners_img, _ = det.rm_text(org, corners_img, ['img' for i in range(len(corners_img))])
            corners_compo, compos_class = det.rm_text(org, corners_compo, compos_class)

        # *** Step 8 *** merge overlapped components
        # corners_img = det.rm_img_in_compo(corners_img, corners_compo)
        corners_img, _ = det.merge_corner(org, corners_img, ['img' for i in range(len(corners_img))], is_merge_nested_same=False)
        corners_compo, compos_class = det.merge_corner(org, corners_compo, compos_class, is_merge_nested_same=True)

        return corners_block, corners_img, corners_compo, compos_class

    # *** used for img element inspection ***
    # only consider rectangular components
    else:
        boundary_rec, boundary_non_rec = det.boundary_detection(binary)
        corners_rec = det.get_corner(boundary_rec)
        corners_block, corners_img, corners_compo = det.block_or_compo(org, binary, corners_rec)
        compos = seg.clipping(org, corners_compo)
        compos_class = clf.predict(compos)
        corners_compo, compos_class = det.strip_img(corners_compo, compos_class, corners_img)

        return corners_block, corners_compo, compos_class


def save(org, binary, corners_block, corners_img, corners_compo, compos_class, output_path_label, output_path_img_drawn, output_path_img_bin):
    # *** Step 10 *** post-processing: remove img elements from original image and segment into smaller size
    # draw results
    draw_bounding = draw.draw_bounding_box_class(org, corners_compo, compos_class)
    draw_bounding = draw.draw_bounding_box_class(draw_bounding, corners_block, ['block' for i in range(len(corners_block))])
    draw_bounding = draw.draw_bounding_box_class(draw_bounding, corners_img, ['img' for i in range(len(corners_img))])
    # save results
    cv2.imwrite(output_path_img_bin, binary)
    cv2.imwrite(output_path_img_drawn, draw_bounding)
    file.save_corners_json(output_path_label, corners_compo, compos_class, new=True)
    file.save_corners_json(output_path_label, corners_block, ['block' for i in range(len(corners_block))], new=False)
    file.save_corners_json(output_path_label, corners_img, ['img' for i in range(len(corners_img))], new=False)


def uied(input_path_img, output_path_label, output_path_img_drawn, output_path_img_bin, img_section):
    print('UIED for', input_path_img)
    org, binary = pre_processing(input_path_img, img_section)
    corners_block, corners_img, corners_compo, compos_class = processing(org, binary, clf)
    save(org, binary, corners_block, corners_img, corners_compo, compos_class, output_path_label, output_path_img_drawn, output_path_img_bin)
    print('*** UI Detection Complete ***')



