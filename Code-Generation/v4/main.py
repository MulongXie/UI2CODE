import numpy as np
import pandas as pd

from Compos_DF import ComposDF
from Compo_HTML import *
from Block import *
import draw

name = 'data/9'
compos = ComposDF(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape

compos.repetitive_group_recognition()    # group_nontext, group_text
compos.pair_groups()                     # pair, pair_to
compos.list_item_partition()             # list
