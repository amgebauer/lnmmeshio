from ..ioutils import line_option_list, read_int, read_option_item


class Component:
    def __init__(self, expression, pos):
        self.expression = expression
        self.pos = pos

    def write(self, dest):
        dest.write("{0}\n".format(self.get_line()))

    def get_line(self):
        d = {"COMPONENT": self.pos, "FUNCTION": self.expression}
        return line_option_list(d)

    @staticmethod
    def read_component(line):
        pos = read_int(line, "COMPONENT")

        if pos is None:
            return None

        expression = read_option_item(line, "FUNCTION")[0]
        component = Component(expression, pos)

        return component
