from ..ioutils import read_int, read_option_item
from .linear_interpolation_variable import LinearInterpolationVariable


def read_variable(line):
    pos = read_int(line, "VARIABLE")

    if pos != 0:
        raise RuntimeError("Only one component is implemented for variables")

    vartype = read_option_item(line, "TYPE")[0]

    if vartype == "linearinterpolation":
        return LinearInterpolationVariable.read_variable(line)
    else:
        raise NotImplementedError(
            "The variable type {0} is not implemented yet!".format(vartype)
        )
