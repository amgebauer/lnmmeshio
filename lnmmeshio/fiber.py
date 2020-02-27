import numpy as np
from .ioutils import (
    write_title,
    write_option_list,
    write_option,
    read_option_item,
    read_next_option,
    read_next_key,
    read_next_value,
    line_option_list,
)

"""
Class that holds all information of fibers
"""


class Fiber:
    # defintion of different fibers (add if more are necessary)
    TypeFiber1: str = "fiber1"
    TypeFiber2: str = "fiber2"
    TypeCir: str = "cir"
    TypeTan: str = "tan"

    """
    Initialize fiber vector in direction of fib

    Args:
        fib: Unit vector pointing in fiber direction np.array((3))
    """

    def __init__(self, fib: np.array):
        self.fiber = fib

    """
    Gets the corresponding line in the dat file

    Args:
        inp_type: type of fiber (defined as static variable)
    """

    def get_line(self, inp_type):
        ftype = None

        if inp_type == Fiber.TypeFiber1:
            ftype = "FIBER1"
        elif inp_type == Fiber.TypeFiber2:
            ftype = "FIBER2"
        elif inp_type == Fiber.TypeCir:
            ftype = "CIR"
        elif inp_type == Fiber.TypeTan:
            ftype = "TAN"
        else:
            raise ValueError("Unknown fiber type {0}".format(inp_type))

        return line_option_list({ftype: self.fiber})

    """
    Writes the corresponding section in the dat file into the stream type variable dest

    Args:
        dest: stream variable where to write the fiber
        inp_type: type of fiber (defined as static variable)
    """

    def write(self, dest, inp_type):
        dest.write(self.get_line(inp_type))

    """
    Returns the corresponding fiber type enum from the definition in the dat file

    Args:
        fstr: Fiber name as defined in the dat file
    
    Returns:
        Fiber enum as defined on top of the class
    """

    @staticmethod
    def get_fiber_type(fstr: str):
        if fstr == "FIBER1":
            return Fiber.TypeFiber1
        elif fstr == "FIBER2":
            return Fiber.TypeFiber2
        elif fstr == "CIR":
            return Fiber.TypeCir
        elif fstr == "TAN":
            return Fiber.TypeTan
        else:
            return None

    """
    Parses the fibers from the line and returns a dict of fiber objects

    Args:
        line: String of the line
    
    Returns:
        dict with fiber type as key and fiber object as value
    """

    @staticmethod
    def parse_fibers(line: str) -> dict:
        fibs: dict = {}
        if "FIBER1" in line:
            fibs[Fiber.TypeFiber1] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER1", num=3)[0]])
            )

        if "FIBER2" in line:
            fibs[Fiber.TypeFiber2] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER2", num=3)[0]])
            )

        if "CIR" in line:
            fibs[Fiber.TypeCir] = Fiber(
                np.array([float(i) for i in read_option_item(line, "CIR", num=3)[0]])
            )

        if "TAN" in line:
            fibs[Fiber.TypeTan] = Fiber(
                np.array([float(i) for i in read_option_item(line, "TAN", num=3)[0]])
            )

        return fibs
