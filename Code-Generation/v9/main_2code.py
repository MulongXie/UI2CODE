import numpy as np
import pandas as pd
import cv2

from obj.Compos_DF import ComposDF
from obj.Compo_HTML import *
from obj.List import *
from obj.Block import *
import lib.draw as draw
from obj.Page import Page


def code_generation(img_path, detection_json_path, output_page_path):
    compos = ComposDF(detection_json_path, img_path)
    img = compos.img.copy()
    img_shape = compos.img_shape
    img_re = cv2.resize(img, img_shape)

    # ***Step 1*** repetitive list recognition
    compos.repetitive_group_recognition()    # group_nontext, group_text
    compos.pair_groups()                     # group_pair, pair_to, group
    compos.list_item_partition()             # list_item
    compos.visualize_block('group')
    compos.visualize_block('group_pair')

    # ***Step 2*** mark compos in same group as a single list, mark compos in same group_pair as a multiple list
    lists, non_listed_compos = gather_lists_by_pair_and_group(compos.compos_dataframe[1:])
    generate_lists_html_css(lists)
    # compos.visualize_block('group')

    # ***Step 3*** slice compos as blocks
    compos_html = [li.list_obj for li in lists] + non_listed_compos
    blocks, non_blocked_compos = slice_blocks(compos_html, 'v')
    visualize_blocks(blocks, img, img_shape)
    blocks[2].visualize_sub_blocks_and_compos(img_re, recursive=True)

    # ***Step 4*** assembly html and css as web page
    page = Page()
    for block in blocks:
        page.add_compo(block.html_script, block.css_script)
    page.export(directory=output_page_path)
