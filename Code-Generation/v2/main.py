import numpy as np
import pandas as pd

from Compos_DF import ComposDF

name = 'data/9'
compos = ComposDF(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape

compos.repetitive_group_recognition()
compos.pair_groups()
compos.list_item_partition()

compos.visualize_block('pair')