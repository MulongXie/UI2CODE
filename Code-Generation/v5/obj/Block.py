import pandas as pd
import cv2
from obj.Compo_HTML import CompoHTML

block_id = 0


def slice_blocks(compos_html, direction='v'):
    '''
    Vertically or horizontally scan compos
    :param compos_html: CompoHTML objects, including elements and lists
    :return blocks: list of [block], block: list of [CompoHTML objects]
    '''
    blocks = []
    block_compos = []
    global block_id

    dividers = []
    divider = -1
    if direction == 'v':
        compos_html.sort(key=lambda x: x.top)
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

    elif direction == 'h':
        compos_html.sort(key=lambda x: x.left)
        for compo in compos_html:
            # new block
            if divider < compo.left:
                dividers.append(compo.left)
                divider = compo.right
                dividers.append(divider)
                if len(block_compos) > 0:
                    blocks.append(Block(block_id, block_compos))
                    block_id += 1
                    block_compos = []
            # extend block
            elif compo.left < divider < compo.right:
                divider = compo.right
                dividers[-1] = divider
            block_compos.append(compo)

    blocks.append(Block(block_id, block_compos))
    return blocks


def blocks_slice_children(blocks):
    for block in blocks:
        block.slice_children_block()


def visualize_blocks(blocks, img, img_shape):
    board = cv2.resize(img, img_shape)
    for block in blocks:
        board = block.visualize(board, img_shape, show=False)
    cv2.imshow('compos', board)
    cv2.waitKey()
    cv2.destroyWindow('compos')


class Block:
    def __init__(self, block_id, compos):
        self.block_id = block_id
        self.compos = compos                # list of CompoHTML objs
        self.block_obj = None               # CompoHTML obj
        self.block_img = None
        self.block_children = []                  # list of Block objs

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

    def slice_children_block(self):
        self.block_children = slice_blocks(self.compos, 'h')

    def clip_block_img(self, org, show=False):
        self.block_img = org[self.top: self.bottom, self.left: self.right]
        if show:
            self.show_block_img()

    def show_block_img(self):
        cv2.imshow('block', self.block_img)
        cv2.waitKey()
        cv2.destroyWindow('block')

    def visualize(self, img=None, img_shape=None, flag='line', show=True):
        fill_type = {'line': 2, 'block': -1}
        img_shape = img_shape
        board = cv2.resize(img, img_shape)
        board = cv2.rectangle(board, (self.left, self.top), (self.right, self.bottom), (0, 255, 0), fill_type[flag])
        if show:
            cv2.imshow('compo', board)
            cv2.waitKey()
            cv2.destroyWindow('compo')
        return board