import numpy as np
import pandas as pd

from obj.Compos_DF import ComposDF
from obj.Compo_HTML import *
from obj.List import *
from obj.Block import *
import lib.draw as draw
from obj.Page import Page

name = 'data/9'
compos = ComposDF(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape
img_re = cv2.resize(img, img_shape)
cv2.imshow('img', img_re)

compos.repetitive_group_recognition()    # group_nontext, group_text
compos.pair_groups()                     # pair, pair_to, group
compos.list_item_partition()             # list_item
compos.visualize_block('group')
compos.visualize_block('pair')

lists, non_listed_compos = gather_lists_by_pair_and_group(compos.compos_dataframe[1:])
generate_lists_html_css(lists)
# compos.visualize_block('group')
compos_html = [li.list_obj for li in lists] + non_listed_compos
blocks, non_blocked_compos = slice_blocks(compos_html, 'v')
visualize_blocks(blocks, img, img_shape)