import pandas as pd
import numpy as np

from obj.CSS import CSS
from obj.HTML import HTML
from obj.Compo_HTML import CompoHTML
import lib.draw as draw

tag_map = {'Compo': 'div', 'Text': 'div', 'Block': 'div'}


def gather_lists_by_pair_and_group(compos):
    '''
    :param compos: type of dataframe
    :return: lists: [list_obj]
             non_list_compos: [compoHTML]
    '''
    lists = []
    non_list_compos = []
    groups = compos.groupby('pair').groups
    list_id = 0
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(list_id, compos.loc[groups[i]], 'multiple', compos.loc[groups[i][0]]['alignment_in_group']))
        list_id += 1
        compos = compos.drop(list(groups[i]))

    groups = compos.groupby('group').groups
    for i in groups:
        if i == -1 or len(groups[i]) == 1:
            continue
        lists.append(List(list_id, compos.loc[groups[i]], 'single', compos.loc[groups[i][0]]['alignment_in_group']))
        list_id += 1
        compos = compos.drop(list(groups[i]))

    for i in range(len(compos)):
        compo = compos.iloc[i]
        compo_html = CompoHTML(compo_id=compo['id'], compo_df=compo, html_tag=tag_map[compo['class']], html_id=tag_map[compo['class']] + '-' + str(compo['id']))
        non_list_compos.append(compo_html)
    return lists, non_list_compos


def generate_lists_html_css(lists):
    for li in lists:
        li.generate_html_list()

        li.generate_css_by_element_group()
        li.generate_css_by_item_group()
        li.generate_css_list_item()


class List:
    def __init__(self, list_id, compos_df, list_type, list_alignment):
        self.list_id = list_id
        self.compos_df = compos_df

        self.list_type = list_type              # multiple: multiple elements in one list-item; single: one element in one list-item
        self.list_alignment = list_alignment    # same as alignment_in_group
        self.list_obj = None                    # CompoHTML obj

        self.compos_html = {}                   # list of children CompoHTML objects
        self.compos_css = {}                    # list of linked CSS objects
        self.html_script = ''
        self.css_script = ''

    '''
    ******************************
    ******* HTML Generation ******
    ******************************
    '''
    def generate_html_list(self):
        lis = []
        if self.list_type == 'multiple':
            groups = self.compos_df.groupby('list_item').groups
            for i in groups:
                list_items = self.compos_df.loc[groups[i]]
                items = []
                items_id = []
                for j in range(len(list_items)):
                    # html of items
                    item = list_items.iloc[j]
                    compo_id = item['id']
                    self.compos_html[compo_id] = CompoHTML(compo_id=compo_id, compo_df=item, html_tag=tag_map[item['class']], html_class_name=item['group'])
                    items.append(self.compos_html[compo_id])
                    items_id.append(str(compo_id))

                # html of list-items
                li_id = 'li-' + '-'.join(sorted(items_id))
                self.compos_html[li_id] = CompoHTML(compo_id=li_id, compo_df=list_items, html_tag='li', children=items, html_class_name='li-' + str(self.list_id))
                lis.append(self.compos_html[li_id])

        elif self.list_type == 'single':
            for i in range(len(self.compos_df)):
                item = self.compos_df.iloc[i]
                compo_id = item['id']
                self.compos_html[compo_id] = CompoHTML(compo_id=compo_id, compo_df=item, html_tag=tag_map[item['class']], html_class_name=item['group'])
                li_id = 'li-' + str(compo_id)
                self.compos_html[li_id] = CompoHTML(compo_id=li_id, compo_df=item, html_tag='li', children=self.compos_html[compo_id], html_class_name='li-' + str(self.list_id))
                lis.append(self.compos_html[li_id])

        self.list_obj = CompoHTML(compo_id='ul-' + str(self.list_id), compo_df=self.compos_df, html_tag='ul', children=lis, html_id='ul-' + str(self.list_id))
        self.html_script = self.list_obj.html_script

    '''
    ******************************
    ******* CSS Generation *******
    ******************************
    '''
    def assembly_css(self):
        self.css_script = ''
        for i in self.compos_css:
            self.css_script += self.compos_css[i].css_script
        self.list_obj.css = self.compos_css

    def generate_css_by_element_group(self):
        '''
        set css style for each group
        css is defined by class, which same as group name in compo_df
        '''
        self.compos_css['ul'] = CSS('ul', list_style='None', padding_left='0', clear='left')
        compos = self.compos_df
        groups = compos.groupby('group').groups
        backgrounds = {'Compo': 'grey', 'Text': 'green'}
        for i in groups:
            self.compos_css['.' + i] = CSS('.' + i,
                                           width=str(int(compos.loc[groups[i], 'width'].mean())) + 'px',
                                           height=str(int(compos.loc[groups[i], 'height'].mean())) + 'px',
                                           background=backgrounds[compos.loc[groups[i][0], 'class']])
        self.assembly_css()

    def generate_css_by_item_group(self):
        def sort_item_groups():
            '''
            from left to right for vertical list groups / from top to bottom for horizontal groups
            :return: [(group name, compo ids in the group, left/top)]
            '''
            groups = compos.groupby('group').groups
            s_groups = []
            if self.list_alignment == 'v':
                for i in groups:
                    s_groups.append((i, groups[i], compos.loc[groups[i], 'column_min'].min()))
            elif self.list_alignment == 'h':
                for i in groups:
                    s_groups.append((i, groups[i], compos.loc[groups[i], 'row_min'].min()))
            s_groups = sorted(s_groups, key=lambda k: k[2])
            return s_groups

        compos = self.compos_df
        if self.list_type == 'multiple':
            sorted_groups = sort_item_groups()
            ids = [s[1] for s in sorted_groups]
            if self.list_alignment == 'v':
                self.compos_css['.' + sorted_groups[0][0]].add_attrs(float='left')
                for i in range(1, len(sorted_groups)):
                    self.compos_css['.' + sorted_groups[i][0]].add_attrs(margin_left=str(int(compos.loc[ids[i], 'column_min'].min() - compos.loc[ids[i-1], 'column_max'].max())) + 'px',
                                                                         float='left')
            if self.list_alignment == 'h':
                for i in range(1, len(sorted_groups)):
                    self.compos_css['.' + sorted_groups[i][0]].add_attrs(margin_top=str(int(compos.loc[ids[i], 'row_min'].min() - compos.loc[ids[i-1], 'row_max'].max())) + 'px')
        self.assembly_css()

    def generate_css_list_item(self):
        def sort_list_item():
            '''
            from top to bottom for vertical list groups / from left to right for horizontal groups
            :return: [(group name, compo ids in the group, top/left, bottom/right)]
            '''
            groups = compos.groupby('list_item').groups
            s_groups = []
            if self.list_alignment == 'v':
                for i in groups:
                    s_groups.append((compos.loc[groups[i][0], 'group'], groups[i], compos.loc[groups[i], 'row_min'].min(), compos.loc[groups[i], 'row_max'].max()))
            elif self.list_alignment == 'h':
                for i in groups:
                    s_groups.append((compos.loc[groups[i][0], 'group'], groups[i], compos.loc[groups[i], 'column_min'].min(), compos.loc[groups[i], 'column_max'].max()))
            s_groups = sorted(s_groups, key=lambda k: k[2])
            return s_groups

        compos = self.compos_df
        name = '.li-' + str(self.list_id)

        if self.list_type == 'multiple':
            sorted_groups = sort_list_item()
            gaps = []
            for i in range(1, len(sorted_groups)):
                gaps.append(sorted_groups[i][2] - sorted_groups[i-1][3])
            # set css attrs
            margin = int(max(gaps))     # set the margin as the max gap among lis
            if self.list_alignment == 'v':
                height = max([compos.loc[g[1], 'height'].max() for g in sorted_groups])  # set the height of the li as the highest element
                self.compos_css[name] = CSS(name, margin_top=str(margin) + 'px', height=str(height) + 'px')
            elif self.list_alignment == 'h':
                height = max([sum(compos.loc[g[1], 'height']) for g in sorted_groups])
                self.compos_css[name] = CSS(name, margin_left=str(margin) + 'px', height=str(height) + 'px', float='left')

        elif self.list_type == 'single':
            if self.list_alignment == 'v':
                margin = 0
                for i in range(1, len(compos)):
                    margin = max(margin, compos.iloc[i]['row_min'] - compos.iloc[i - 1]['row_max'])
                self.compos_css[name] = CSS(name, margin_top=str(margin))

            elif self.list_alignment == 'h':
                margin = 0
                for i in range(1, len(compos)):
                    margin = max(margin, compos.iloc[i]['column_min'] - compos.iloc[i - 1]['column_max'])
                self.compos_css[name] = CSS(name, margin_left=str(margin) + 'px', float='left')

        self.assembly_css()
