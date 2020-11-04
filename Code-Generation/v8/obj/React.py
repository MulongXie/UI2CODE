
def assembly_compos_react(compos):
    react_page = 'import React from "react";\n'
    react_compo_names = []
    for compo in compos:
        react_compo_names.append(compo.react.react_compo_name)
        react_page += compo.react.assembly_react(compo.css) + '\n'
    react_page += 'export default ' + ','.join(react_compo_names) + ';'
    return react_page


class React:
    def __init__(self, tag, react_compo_name='', **kwargs):
        self.tag = tag
        self.attrs = kwargs
        self.react_compo_name = react_compo_name.capitalize()
        self.react_compo_script = ''       # in react component class

        self.class_name = self.init_by_input_attr('class_name')
        self.id = self.init_by_input_attr('id')
        self.children = self.init_by_input_attr('children', '')  # react script
        self.close = True

        self.react_script = None
        self.generate_react_html()

    def init_by_input_attr(self, attr, non_exist_alt=None):
        if attr in self.attrs:
            return self.attrs[attr]
        return non_exist_alt

    def generate_react_html(self):
        # start
        react = "<" + self.tag
        if self.id is not None:
            if self.react_compo_name is None:
                self.react_compo_name = self.id.replace('-', '').capitalize()
            react += " style={this.state.css." + self.id.replace('-', '') + "}"
        if self.class_name is not None:
            react += " style={this.state.css." + self.class_name.replace('-', '') + "}"
        react += ">\n"

        # body
        if self.children is not None:
            # indent
            children = '\t' + self.children.replace('\n', '\n\t')
            react += children[:-1]

        # close
        if self.close:
            react += "</" + self.tag + ">\n"
        else:
            react[-1] = '/>\n'
        self.react_script = react

    def add_child(self, child):
        '''
        :param child: string, html script
        '''
        self.children += child
        self.generate_react_html()

    def assembly_react(self, css_dict):
        def indent(s, no):
            lines = s.split('\n')
            result = ''
            for line in lines:
                result += '\t' * no + line + '\n'
            return result

        head = "class " + self.react_compo_name + ' extends React.Component{' + '\n' + \
            indent('constructor(){', 1) + \
            indent('super();', 2)

        style = 'this.state = {css:{\n'
        for tag in css_dict:
            # refactor css tag
            s = tag.split('-')
            if s[0][0] in ['.', '#']:
                s[0] = s[0][1:]
            new_tag = ''.join(s)
            # refactor css content
            css = css_dict[tag].css_script
            new_css = ''
            s = css.split('\n')
            for line in s[1:-2]:
                line = line.replace('\t', '')
                c = line.split(':')
                new_css += ':'.join([c[0], c[1][:-1]]) + ',\n'
            new_css = new_tag + ':{\n' + indent(new_css[:-2], 1) + '},\n'
            style += indent(new_css, 1)
        style = style[:-4] + '\n}'
        style = indent(style, 2)

        render = indent('render(){', 1) + \
            indent('return (', 2) + \
            indent(self.react_script, 3) + \
            indent(')', 2) + \
            indent('}', 1)

        react_compo = head + '\n' + style + indent('}', 1) + render + '}\n'
        self.react_compo_script = react_compo
        return react_compo
