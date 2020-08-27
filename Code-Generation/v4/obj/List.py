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


def generate_lists_html_css(lists):
    for li in lists:
        li.generate_html_list()

        li.generate_css_by_element()
        li.generate_css_by_item_group()
        li.generate_css_by_list_item()


class List:
    def __init__(self, compos_df, list_type, list_alignment):
        self.compos_df = compos_df
        self.list_type = list_type
        self.list_alignment = list_alignment
        self.list_items = []

        # self.compos_html = {}
        self.compos_css = {}
        self.list_html = ''
        self.list_css = ''

    '''
    ******************************
    ******* HTML Generation ******
    ******************************
    '''
    def generate_html_list(self):
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

    '''
    ******************************
    ******* CSS Generation *******
    ******************************
    '''
    def generate_css_by_element(self):
        '''
        css is defined by class, which same as group name in compo_df
        '''
        compos = self.compos_df
        groups = compos.groupby('group').groups
        backgrounds = {'Compo': 'grey', 'Text': 'green'}
        for i in groups:
            c = CSS('.' + i,
                    width=str(int(compos.loc[groups[i], 'width'].mean())) + 'px',
                    height=str(int(compos.loc[groups[i], 'height'].mean())) + 'px',
                    background=backgrounds[compos.loc[groups[i][0], 'class']])
            self.compos_css['.' + i] = c
        for i in self.compos_css:
            self.list_css += self.compos_css[i].css

    def generate_css_by_item_group(self):
        compos = self.compos_df

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

        if self.list_type == 'multiple':
            sorted_groups = sort_item_groups()
            ids = [s[1] for s in sorted_groups]
            for i in range(1, len(sorted_groups)):
                name = '.' + sorted_groups[i][0]
                if self.list_alignment == 'v':
                    self.compos_css[name].add_attrs(margin_left=str(int(compos.loc[ids[i], 'column_min'].min() - compos.loc[ids[i-1], 'column_max'].max())) + 'px')
                if self.list_alignment == 'h':
                    self.compos_css[name].add_attrs(margin_top=str(int(compos.loc[ids[i], 'row_min'].min() - compos.loc[ids[i-1], 'row_max'].max())) + 'px')
        self.list_css = ''
        for i in self.compos_css:
            self.list_css += self.compos_css[i].css

    def generate_css_by_list_item(self):
        compos = self.compos_df

        def sort_list_item():
            '''
            from top to bottom for vertical list groups / from left to right for horizontal groups
            :return: [(group name, compo ids in the group, left/top)]
            '''
            groups = compos.groupby('list_item').groups
            s_groups = []
            if self.list_alignment == 'v':
                for i in groups:
                    s_groups.append((compos.loc[groups[i][0], 'group'], groups[i], compos.loc[groups[i], 'row_min'].min()))
            elif self.list_alignment == 'h':
                for i in groups:
                    s_groups.append((compos.loc[groups[i][0], 'group'], groups[i], compos.loc[groups[i], 'column_min'].min()))
            s_groups = sorted(s_groups, key=lambda k: k[2])
            return s_groups

        if self.list_type == 'multiple':
            sorted_groups = sort_list_item()
            ids = [s[1] for s in sorted_groups]
            n1 = compos.loc[ids[0][0]]['group'].split('-')
            n2 = compos.loc[ids[0][1]]['group'].split('-')
            name = 'li-' + n1[1] + '-' + n2[1] if n1[0] == 't' else 'li-' + n2[1] + '-' + n1[1]
            print(name)
            # if self.list_alignment == 'v':
            #     self.compos_css[name].add_attrs(margin_top=str(int(compos.loc[ids[1], 'row_min'].min() - compos.loc[ids[0], 'row_max'].max())) + 'px')
            # if self.list_alignment == 'h':
            #     self.compos_css[name].add_attrs(margin_left=str(int(compos.loc[ids[1], 'column_min'].min() - compos.loc[ids[0], 'column_max'].max())) + 'px')

        #     name = '.' + sorted_groups[i][0]
        #     if self.list_alignment == 'v':
        #         self.compos_css[name].add_attrs(margin_top=str(int(compos.loc[ids[i], 'row_min'].min() - compos.loc[ids[i - 1], 'row_max'].max())) + 'px')
        #     if self.list_alignment == 'h':
        #         self.compos_css[name].add_attrs(margin_left=str(int(compos.loc[ids[i], 'column_min'].min() - compos.loc[ids[i-1], 'column_max'].max())) + 'px')
        # self.list_css = ''
        # for i in self.compos_css:
        #     self.list_css += self.compos_css[i].css
