import pandas as pd
import json

from obj.CSS import CSS
from obj.HTML import HTML


class CompoHTML:
    def __init__(self, compo_df=None, compo_id=None, html_id=None, html_class_name=None, children=None, parent=None):
        self.compo_df = compo_df
        self.compo_id = compo_df['id'] if compo_id is None and compo_df is not None else compo_id

        self.children = children if children is not None else []    # CompoHTML objs
        self.parent = parent                                        # CompoHTML obj

        self.html_id = html_id
        self.html_class_name = html_class_name
        self.html_tag = None
        self.html_tag_map = {'Compo': 'div', 'Text': 'div', 'Block': 'div'}
        self.html = None    # HTML obj
        self.css = []       # CSS objs, a compo may have multiple css styles through linking to multiple css classes
        self.init_html()

    def init_html(self):
        category = self.compo_df['class']
        self.html_tag = self.html_tag_map[category]
        self.html = HTML(tag=self.html_tag, id=self.html_id, class_name=self.html_class_name)

    def add_child(self, child):
        self.children.append(child)
        self.html.add_child(child.html.html_script)
