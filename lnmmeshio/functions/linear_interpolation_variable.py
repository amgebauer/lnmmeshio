from ..ioutils import (
    line_option_list,
    read_floats,
    read_int,
    read_ints,
    read_option_item,
    write_option_list,
)
from .variable import BaseVariable


class LinearInterpolationVariable(BaseVariable):
    def __init__(self, name: str, times, values):
        super(LinearInterpolationVariable, self).__init__(name)
        self.times = times
        self.values = values

    def get_line(self):
        line = super(LinearInterpolationVariable, self).get_line()

        d = {
            "TYPE": "linearinterpolation",
            "NUMPOINTS": len(self.times),
            "TIMES": self.times,
            "VALUES": self.values,
        }
        return "{0} {1}".format(line, line_option_list(d))

    def write(self, dest):
        dest.write("{0}\n".format(self.get_line()))

    @staticmethod
    def read_variable(line):
        numpoints = read_int(line, "NUMPOINTS")

        times = read_floats(line, "TIMES", numpoints)
        values = read_floats(line, "VALUES", numpoints)

        name = read_option_item(line, "NAME")[0]
        if name is None:
            raise RuntimeError(
                "Expecting NAME of variable to be given. Line is {0}".format(line)
            )

        return LinearInterpolationVariable(name, times, values)
