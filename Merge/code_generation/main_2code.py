import numpy as np
import pandas as pd
from os.path import join as pjoin

from obj.Compos_DF import ComposDF
from obj.Compo_HTML import *
from obj.List import *
from obj.Block import *
from obj.Group import *
from obj.React import *
from obj.Page import *
from obj.Tree import *
import lib.draw as draw
from lib.list_item_gethering import gather_lists_by_pair_and_group


def generate_code(input_name='code_generation/data/input/9', output_dir='code_generation/data/output'):
    compos = ComposDF(json_file=input_name + '-new.json', img_file=input_name + '.png')

    # ***Step 1*** repetitive list recognition
    compos.repetitive_group_recognition()    # group_nontext, group_text
    check_valid_group_by_interleaving(compos.compos_dataframe)
    compos.pair_groups()                     # group_pair, pair_to, group
    compos.list_item_partition()             # list_item
    # compos.visualize_block('group')
    # compos.visualize_block('group_pair')

    # ***Step 2*** mark compos in same group as a single list, mark compos in same group_pair as a multiple list
    # Start generating HTML and CSS here
    lists, non_listed_compos = gather_lists_by_pair_and_group(compos.compos_dataframe[1:])
    generate_lists_html_css(lists)
    # visualize_lists(img_re, lists)

    # ***Step 3*** slice compos as blocks
    compos_html = [li.list_obj for li in lists] + non_listed_compos
    blocks = build_layout_blocks(compos_html)
    # visualize_CompoHTMLs(compos_html, img_re)
    # visualize_blocks(blocks, img, img_shape)

    # ***Step 4*** assembly html and css as web page, and react program
    html, css = export_html_and_css(blocks, export_dir=pjoin(output_dir, 'page'))
    blk, index = export_react_program(blocks, export_dir=pjoin(output_dir, 'react'))
    tree = export_tree(blocks, export_dir=pjoin(output_dir, 'tree'))
