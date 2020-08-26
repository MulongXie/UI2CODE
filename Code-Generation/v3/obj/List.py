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
        li.generate_css_list()


class List:
    def __init__(self, compos_df, list_type, list_alignment):
        self.compos_df = compos_df
        self.list_type = list_type
        self.list_alignment = list_alignment

        self.list_html = None
        self.list_css = None

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

    def sort_item_groups(self):
        '''
        :return: [(group name, compo ids in the group, left/top)]
        ‘left and right for vertical list groups / top and bottom for horizontal groups’
        '''
        compos = self.compos_df
        groups = compos.groupby('group').groups
        sorted_groups = []
        if self.list_alignment == 'v':
            for i in groups:
                sorted_groups.append((i, groups[i], compos.loc[groups[i], 'column_min'].min()))
        elif self.list_alignment == 'h':
            for i in groups:
                sorted_groups.append((i, groups[i], compos.loc[groups[i], 'row_min'].min()))
        sorted_groups = sorted(sorted_groups, key=lambda k: k[2])
        return sorted_groups

    def generate_css_list(self):
        compos = self.compos_df
        css = ''
        backgrounds = {'Compo': 'grey', 'Text': 'green'}
        if self.list_type == 'multiple':
            sorted_groups = self.sort_item_groups()
            ids = [s[1] for s in sorted_groups]
            for i in range(0, len(sorted_groups)):
                c = CSS('.' + sorted_groups[i][0],
                        width=str(int(compos.loc[ids[i], 'width'].mean())) + 'px',
                        height=str(int(compos.loc[ids[i], 'height'].mean())) + 'px',
                        background=backgrounds[compos.loc[ids[i][0], 'class']])
                if i > 0 and self.list_alignment == 'v':
                    c.add_attrs(margin_left=str(int(compos.loc[ids[i], 'column_min'].min() - compos.loc[ids[i-1], 'column_max'].max())) + 'px')
                if i > 0 and self.list_alignment == 'h':
                    c.add_attrs(margin_top=str(int(compos.loc[ids[i], 'row_min'].min() - compos.loc[ids[i-1], 'row_max'].max())) + 'px')
                css += c.css
        self.list_css = css
