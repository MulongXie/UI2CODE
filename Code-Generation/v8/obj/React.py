
class React:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.attrs = kwargs

        self.class_name = self.init_by_input_attr('class_name')
        self.id = self.init_by_input_attr('id')
        self.children = self.init_by_input_attr('children', '')  # react script
        self.close = True

        self.react_script = None
        self.generate_react()

    def init_by_input_attr(self, attr, non_exist_alt=None):
        if attr in self.attrs:
            return self.attrs[attr]
        return non_exist_alt

    def generate_react(self):
        # start
        react = "<" + self.tag
        if self.id is not None:
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
        self.generate_react()
