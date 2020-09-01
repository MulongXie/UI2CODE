import pandas as pd
from obj.Compo_HTML import CompoHTML


def gather_blocks(compos):
    blocks = []
    groups = compos.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        block_compos = compos.loc[groups[i]]
        block_compos.rename({"pair": "list"}, axis=1, inplace=True)
        block_compos.rename({"group": "block"}, axis=1, inplace=True)
        block = Block(i, block_compos)
        blocks.append(block)
    return blocks


def slice_blocks(compos):
    '''
    :param compos: CompoHTML objects, including elements and lists
    '''
    lines = []
    line = -1
    for compo in compos:
        if line < compo.top:
            lines.append(compo.top)
            line = compo.bottom
            lines.append(line)
        elif compo.top < line < compo.bottom:
            line = compo.bottom
            lines[-1] = line


class Block:
    def __init__(self, block_id, compos_df, children=None, children_alignment=None):
        self.block_id = block_id
        self.compos_df = compos_df
        self.block_html = None                    # CompoHTML obj

        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self.width = None
        self.height = None

        self.children = children
        self.children_alignment = children_alignment

        self.compos_html = {}                     # list of children CompoHTML objects
        self.compos_css = {}                      # list of linked CSS objects
        self.html_script = ''
        self.css_script = ''

    def identify_boundary(self):
        pass
