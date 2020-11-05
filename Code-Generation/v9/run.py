import numpy as np
import pandas as pd

from obj.Compos_DF import ComposDF
from obj.Compo_HTML import *
from obj.List import *
from obj.Block import *
from obj.Group import *
from obj.React import *
from obj.Page import *

name = 'data/input/9'
compos = ComposDF(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape
img_re = cv2.resize(img, img_shape)

# ***Step 1*** repetitive ui compos recognition
compos.repetitive_group_recognition()    # group_nontext, group_text
check_valid_group_by_interleaving(compos.compos_dataframe)
compos.pair_groups()                     # group_pair, pair_to, group
compos.list_item_partition()             # list_item

# ***Step 2*** mark compos in same group as a single list, mark compos in same group_pair as a multiple list
lists, non_listed_compos = gather_lists_by_pair_and_group(compos.compos_dataframe[1:])
generate_lists_html_css(lists)

# ***Step 3*** slice compos as blocks
compos_html = [li.list_obj for li in lists] + non_listed_compos
blocks, non_blocked_compos = slice_blocks(compos_html, 'v')

# ***Step 4*** assembly html and css as web page, and react program
html, css = export_html_and_css(blocks)
blk, index = export_react_program(blocks)