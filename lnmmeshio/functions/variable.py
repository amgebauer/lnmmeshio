from ..ioutils import line_option_list


class BaseVariable:
    def __init__(self, name):
        self.name = name

    def get_line(self):
        d = {"VARIABLE": 0, "NAME": self.name}
        return line_option_list(d)

    def write(self, dest):
        dest.write("{0}\n".format(self.get_line()))
