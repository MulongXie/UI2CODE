import pandas as pd
from obj.CSS import CSS
from obj.HTML import HTML
import lib.draw as draw


def gather_lists(compos):
    lists = []
    groups = compos.groupby('pair').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(compos.loc[groups[i]], 'multiple', compos.loc[groups[i][0]]['alignment_list']))
        compos = compos.drop(list(groups[i]))

    groups = compos.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(compos.loc[groups[i]], 'single', compos.loc[groups[i][0]]['alignment_list']))
    return lists


class List:
    def __init__(self, compos_df, list_type, list_alignment):
        self.compos_df = compos_df
        self.list_type = list_type
        self.list_alignment = list_alignment

        self.list_html = None
        self.list_css = None

    def get_groups_layouts(self):
        '''
        :return: [(group name, left/top, right/bottom, compo class)]
        ‘left and right for vertical list groups / top and bottom for horizontal groups’
        '''
        compos = self.compos_df
        groups = compos.groupby('group').groups
        layouts = []
        if self.list_alignment == 'v':
            for i in groups:
                layouts.append((i, compos.loc[groups[i], 'column_min'].min(), compos.loc[groups[i], 'column_max'].max(), compos.loc[groups[i][0], 'class']))
        elif self.list_alignment == 'h':
            for i in groups:
                layouts.append((i, compos.loc[groups[i], 'row_min'].min(), compos.loc[groups[i], 'row_max'].max(), compos.loc[groups[i][0], 'class']))
        layouts = sorted(layouts, key=lambda k: k[1])
        return layouts

    def generate_list_css(self):
        css = ''
        backgrounds = {'Compo': 'grey', 'Text':'green'}
        if self.list_type == 'multiple':
            groups_layouts = self.get_groups_layouts()
            css += CSS('.' + groups_layouts[0][0], background=backgrounds[groups_layouts[0][3]]).css
            if self.list_alignment == 'v':
                for i in range(1, len(groups_layouts)):
                    css += CSS('.' + groups_layouts[i][0],
                               margin_left=str(int(groups_layouts[i][1] - groups_layouts[i - 1][2])) + 'px',
                               background=backgrounds[groups_layouts[i][3]]).css
            if self.list_alignment == 'h':
                for i in range(1, len(groups_layouts)):
                    css += CSS('.' + groups_layouts[i][0],
                               margin_top=str(int(groups_layouts[i][1] - groups_layouts[i - 1][2])) + 'px',
                               background=backgrounds[groups_layouts[i][3]]).css
        self.list_css = css

    def generate_list_html(self):
        list_html = ''
        tags = {'Compo': 'div', 'Text': 'div'}
        if self.list_type == 'multiple':
            groups = self.compos_df.groupby('list_item').groups
            list_item_html = ''
            for i in groups:
                list_items = self.compos_df.loc[groups[i]]
                elements_html = ''
                for j in range(len(list_items)):
                    item = list_items.iloc[j]
                    # html of elements
                    elements_html += HTML(tag=tags[item['class']], class_name=item['group']).html
                # html of list_items
                list_item_html += HTML(tag='li', children=elements_html).html
            list_html = HTML(tag='ul', children=list_item_html).html

        elif self.list_type == 'single':
            list_item_html = ''
            for i in range(len(self.compos_df)):
                item = self.compos_df.iloc[i]
                elements_html = HTML(tag=tags[item['class']], class_name=item['group']).html
                list_item_html += HTML(tag='li', children=elements_html).html
            list_html = HTML(tag='ul', children=list_item_html).html
        self.list_html = list_html
