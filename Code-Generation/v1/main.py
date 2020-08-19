import numpy as np
from DF_Compos import DF_Compos
from Group import *
from repetition_recog import *
from pairing import *
import draw

name = 'data/9'
compos = DF_Compos(name + '.json', name + '.png')
img = compos.img.copy()
img_shape = compos.img_shape

# recognize repetition
compos_nontext = recog_repetition_nontext(compos, show=False)
compos_text = recog_repetition_text(compos, show=False)

# select all repetitive compos and group them by repetition
groups_nontext, no_groups_nontext = compos_nontext.cvt_groups('group_nontext', 'nontext')
groups_text, no_groups_text = compos_text.cvt_groups('group_text', 'text')
all_groups = groups_nontext + groups_text

# pair differnet repetition to search for possible combination
pairs, no_pairs = pair_matching_within_groups(all_groups)
df_pairs = pair_cvt_df(pairs)

# collect all results in a Dataframe
df_no_groups = no_groups_nontext.append(no_groups_text, sort=False)
df_no_pairs = groups_cvt_df(no_pairs)
df_all = df_no_groups.append(df_no_pairs, sort=False).append(df_pairs, sort=False)

# post processing
df_all = df_all.sort_index()
df_all[list(df_all.filter(like='group'))] = df_all[list(df_all.filter(like='group'))].fillna(-1).astype(int)
df_all['pair'] = df_all['pair'].fillna(-1).astype(int)
draw.visualize_block(img, df_all, img_shape, attr='pair')