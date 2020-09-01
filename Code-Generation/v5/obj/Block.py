import pandas as pd
import cv2
from obj.Compo_HTML import CompoHTML


def slice_blocks(compos_html):
    '''
    Vertically scan compos
    :param compos_html: CompoHTML objects, including elements and lists
    :return blocks: list of [block], block: list of [CompoHTML objects]
    '''
    blocks = []
    block_compos = []
    block_id = 0

    dividers = []
    divider = -1
    for compo in compos_html:
        # new block
        if divider < compo.top:
            dividers.append(compo.top)
            divider = compo.bottom
            dividers.append(divider)

            if len(block_compos) > 0:
                blocks.append(Block(block_id, block_compos))
                block_id += 1
                block_compos = []
        # extend block
        elif compo.top < divider < compo.bottom:
            divider = compo.bottom
            dividers[-1] = divider
        block_compos.append(compo)

    blocks.append(Block(block_id, block_compos))
    return blocks


def visualize_Blocks(blocks, img, img_shape):
    board = cv2.resize(img, img_shape)
    for block in blocks:
        board = block.visualize(board, img_shape, show=False)
    cv2.imshow('compos', board)
    cv2.waitKey()
    cv2.destroyWindow('compos')


class Block:
    def __init__(self, block_id, compos, children=None, children_alignment=None):
        self.block_id = block_id
        self.compos = compos                # list of CompoHTML objs
        self.block_obj = None               # CompoHTML obj

        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self.width = None
        self.height = None

        self.html_script = ''
        self.css_script = ''

        self.init_boundary()

    def init_boundary(self):
        self.top = min(self.compos, key=lambda x: x.top).top
        self.bottom = max(self.compos, key=lambda x: x.bottom).bottom
        self.left = min(self.compos, key=lambda x: x.left).left
        self.right = max(self.compos, key=lambda x: x.right).right

    def visualize(self, img=None, img_shape=None, flag='line', show=True):
        fill_type = {'line':2, 'block':-1}
        img_shape = img_shape
        board = cv2.resize(img, img_shape)
        board = cv2.rectangle(board, (self.left, self.top), (self.right, self.bottom), (0,255,0), fill_type[flag])
        if show:
            cv2.imshow('compo', board)
            cv2.waitKey()
            cv2.destroyWindow('compo')
        return board

    def slice_children_block(self):
        pass