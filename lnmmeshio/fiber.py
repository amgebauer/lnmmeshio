import numpy as np

from .ioutils import (
    line_option_list,
    read_next_key,
    read_next_option,
    read_next_value,
    read_option_item,
    write_option,
    write_option_list,
    write_title,
)


"""
Class that holds all information of fibers
"""


class Fiber:
    # defintion of different fibers (add if more are necessary)
    TypeFiber1: str = "fiber1"
    TypeFiber2: str = "fiber2"
    TypeFiber3: str = "fiber3"
    TypeFiber4: str = "fiber4"
    TypeFiber5: str = "fiber5"
    TypeFiber6: str = "fiber6"
    TypeFiber7: str = "fiber7"
    TypeFiber8: str = "fiber8"
    TypeFiber9: str = "fiber9"
    TypeCir: str = "cir"
    TypeTan: str = "tan"
    TypeRad: str = "rad"
    TypeAxi: str = "axi"

    """
    Initialize fiber vector in direction of fib

    Args:
        fib: Unit vector pointing in fiber direction np.array((3))
    """

    def __init__(self, fib: np.ndarray):
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
        elif inp_type == Fiber.TypeFiber3:
            ftype = "FIBER3"
        elif inp_type == Fiber.TypeFiber4:
            ftype = "FIBER4"
        elif inp_type == Fiber.TypeFiber5:
            ftype = "FIBER5"
        elif inp_type == Fiber.TypeFiber6:
            ftype = "FIBER6"
        elif inp_type == Fiber.TypeFiber7:
            ftype = "FIBER7"
        elif inp_type == Fiber.TypeFiber8:
            ftype = "FIBER8"
        elif inp_type == Fiber.TypeFiber9:
            ftype = "FIBER9"
        elif inp_type == Fiber.TypeCir:
            ftype = "CIR"
        elif inp_type == Fiber.TypeTan:
            ftype = "TAN"
        elif inp_type == Fiber.TypeRad:
            ftype = "RAD"
        elif inp_type == Fiber.TypeAxi:
            ftype = "AXI"
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
        elif fstr == "FIBER3":
            return Fiber.TypeFiber3
        elif fstr == "FIBER4":
            return Fiber.TypeFiber4
        elif fstr == "FIBER5":
            return Fiber.TypeFiber5
        elif fstr == "FIBER6":
            return Fiber.TypeFiber6
        elif fstr == "FIBER7":
            return Fiber.TypeFiber7
        elif fstr == "FIBER8":
            return Fiber.TypeFiber8
        elif fstr == "FIBER9":
            return Fiber.TypeFiber9
        elif fstr == "CIR":
            return Fiber.TypeCir
        elif fstr == "TAN":
            return Fiber.TypeTan
        elif fstr == "AXI":
            return Fiber.TypeAxi
        elif fstr == "RAD":
            return Fiber.TypeRad
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

        if "FIBER3" in line:
            fibs[Fiber.TypeFiber3] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER3", num=3)[0]])
            )

        if "FIBER4" in line:
            fibs[Fiber.TypeFiber4] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER4", num=3)[0]])
            )

        if "FIBER5" in line:
            fibs[Fiber.TypeFiber5] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER5", num=3)[0]])
            )

        if "FIBER6" in line:
            fibs[Fiber.TypeFiber6] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER6", num=3)[0]])
            )

        if "FIBER7" in line:
            fibs[Fiber.TypeFiber7] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER7", num=3)[0]])
            )

        if "FIBER8" in line:
            fibs[Fiber.TypeFiber8] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER8", num=3)[0]])
            )

        if "FIBER9" in line:
            fibs[Fiber.TypeFiber9] = Fiber(
                np.array([float(i) for i in read_option_item(line, "FIBER9", num=3)[0]])
            )

        if "CIR" in line:
            fibs[Fiber.TypeCir] = Fiber(
                np.array([float(i) for i in read_option_item(line, "CIR", num=3)[0]])
            )

        if "TAN" in line:
            fibs[Fiber.TypeTan] = Fiber(
                np.array([float(i) for i in read_option_item(line, "TAN", num=3)[0]])
            )

        if "RAD" in line:
            fibs[Fiber.TypeRad] = Fiber(
                np.array([float(i) for i in read_option_item(line, "RAD", num=3)[0]])
            )

        if "AXI" in line:
            fibs[Fiber.TypeAxi] = Fiber(
                np.array([float(i) for i in read_option_item(line, "AXI", num=3)[0]])
            )

        return fibs
