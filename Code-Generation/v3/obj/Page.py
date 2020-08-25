
class Page:
    def __init__(self, compos_html, compos_css, title='Title'):
        self.compos_html = compos_html
        self.compos_css = compos_css
        self.title = title

        self.html_header = None
        self.html_body = None
        self.html_end = "</body></html>"

        self.page_html = None
        self.page_css = None

    def assembly_html_body(self):
        body = "<body>"
        if type(self.compos_html) is list:
            for html in self.compos_html:
                body += html
        else:
            body += self.compos_html

    def add_compo_html(self, compos_html):
        if type(compos_html) is list:
            for html in compos_html:
                self.html_body += html
        else:
            self.html_body += compos_html
        self.generate_page_html()

    def generate_page_html(self):
        self.html_header = "<!DOCTYPE html>\n<html>\n<head><title>" + self.title + "</title></head>"
        self.page_html = self.html_header + self.html_body + self.html_end

    def generate_page_css(self):
        if type(self.compos_css) is list:
            for css in self.compos_css:

