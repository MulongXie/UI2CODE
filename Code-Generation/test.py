import numpy as np

from DF_Compos import DF_Compos
from Group import *
from repetition_recog import *
from pairing import *
import draw
from List import *
from Block import *

name = 'data/9'
compos = DF_Compos(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape

compos.repetitive_group_recognition()
compos.pair_groups()


groups = compos.compos_dataframe.groupby("pair").groups
blocks = []
for i in groups:
    if i == -1:
        continue
    group = groups[i]
    compos_block = compos.compos_dataframe.loc[list(group)]
    list_items = gather_list_items(compos_block)
    block = Block(i, compos_block, list_items)
    blocks.append(block)