import pandas as pd
import json


class CompoHTML:
    def __init__(self, compo_df, **kwargs):
        self.compo_df = compo_df
        self.attrs = kwargs

        self.class_name = None
        self.html_id = None
        self.tag = None
        self.content = None
        self.close = True

        self.html = None
        self.css = None
        self.generate_html()
        self.generate_css()

    def add_attrs(self, **kwargs):
        self.attrs.update(kwargs)
        self.generate_css()

    def generate_tag(self):
        category = self.compo_df['class']
        if category == 'Compo':
            self.tag = "div"
            self.add_attrs(background='grey')
        elif category == 'Text':
            self.tag = "div"
            self.add_attrs(background='green')

    def generate_css(self):
        css = json.dumps(self.attrs, indent=4)
        css = css.replace('_', '-')
        css = css.replace(',', ';')
        self.css = css

    def generate_html(self):
        self.generate_tag()
        # start
        html = "<" + self.tag
        if self.html_id is not None:
            html += " \"id=" + self.html_id + "\""
        if self.class_name is not None:
            html += " \"class=" + self.class_name + "\""
        html += ">"

        # body
        if self.content is not None:
            html += self.content

        # close
        if self.close:
            html += "</" + self.tag + ">"
        else:
            html[-1] = '/>'

        self.html = html

