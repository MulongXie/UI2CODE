import json


class CSS:
    def __init__(self, name, **kwargs):
        self.name = name
        self.attrs = kwargs

        self.css = None
        self.generate_css()

    def generate_css(self):
        css = json.dumps(self.attrs, indent=4)
        css = css.replace('_', '-')
        css = css.replace(',', ';')
        self.css = self.name + css + '\n'

    def add_attrs(self, attrs):
        self.attrs.update(attrs)
        self.generate_css()
