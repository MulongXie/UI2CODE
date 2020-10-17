import numpy as np
import pandas as pd

from obj.Compos_DF import ComposDF
from obj.Compo_HTML import *
from obj.List import *
from obj.Block import *
from obj.Group import *
import lib.draw as draw
from obj.Page import Page

name = 'data/9'
compos = ComposDF(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape
img_re = cv2.resize(img, img_shape)

# ***Step 1*** repetitive list recognition
compos.repetitive_group_recognition()    # group_nontext, group_text
check_valid_group_by_interleaving(compos.compos_dataframe)
compos.pair_groups()                     # group_pair, pair_to, group
compos.list_item_partition()             # list_item
compos.visualize_block('group')
compos.visualize_block('group_pair')
