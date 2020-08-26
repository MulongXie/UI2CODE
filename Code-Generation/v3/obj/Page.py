import os


class Page:
    def __init__(self, compos_html=None, compos_css=None, title='Title',
                 html_file_name='xml.html', css_file_name='xml.css'):
        self.html_file_name = html_file_name
        self.css_file_name = css_file_name

        if compos_html is None:
            self.compos_html = []
        else:
            self.compos_html = compos_html if type(compos_html) is list else [compos_html]
        if compos_css is None:
            self.compos_css = []
        else:
            self.compos_css = compos_css if type(compos_css) is list else [compos_css]

        self.title = title
        self.html_header = None
        self.html_body = None
        self.html_end = "</body>\n</html>"

        self.page_html = ''
        self.page_css = ''
        self.init_page_html()
        self.init_page_css()

    def init_page_html(self):
        # header
        self.html_header = "<!DOCTYPE html>\n<html>\n<head>\n\t<title>" \
                           + self.title + "</title>\n" \
                           + "<link rel=\"stylesheet\" href=\"" + self.css_file_name + "\">" \
                           + "</head>\n"
        # body
        self.html_body = "<body>\n"
        for html in self.compos_html:
            self.html_body += html
        # assembly
        self.page_html = self.html_header + self.html_body + self.html_end

    def init_page_css(self):
        self.page_css = ''
        for css in self.compos_css:
            self.page_css += css

    def add_compo_html(self, compos_html):
        compos_html = compos_html if type(compos_html) is list else [compos_html]
        self.compos_html += compos_html
        for html in compos_html:
            self.html_body += html
        self.page_html = self.html_header + self.html_body + self.html_end

    def add_compo_css(self, compo_css):
        compo_css = compo_css if type(compo_css) is list else [compo_css]
        self.compos_css += compo_css
        for css in compo_css:
            self.page_css += css

    def add_compo(self, compo_html, compo_css):
        self.add_compo_html(compo_html)
        self.add_compo_css(compo_css)

    def export(self, directory='page', html_file_name='xml.html', css_file_name='xml.css'):
        os.makedirs(directory, exist_ok=True)
        html_path = os.path.join(directory, html_file_name)
        css_path = os.path.join(directory, css_file_name)
        open(html_path, 'w').write(self.page_html)
        open(css_path, 'w').write(self.page_css)
