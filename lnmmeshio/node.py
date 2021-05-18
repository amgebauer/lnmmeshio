import io
from typing import Dict

import numpy as np

from .fiber import Fiber


class Node:
    """
    Class that holds all information of nodes like coords, fibers, nodesets (and additional data)
    """

    def __init__(self, coords: np.ndarray = np.zeros((3))):
        """
        Initialize node at the coordinades coords

        Args:
            coords: np.array((3)) Coordinates of the node
        """
        self.id = None
        self.coords: np.ndarray = coords
        self.fibers: Dict[str, Fiber] = {}

        self.pointnodesets = []
        self.linenodesets = []
        self.surfacenodesets = []
        self.volumenodesets = []
        self.data = {}

    def reset(self):
        """
        Sets the id to None
        """
        self.id = None

    def get_line(self):
        """
        Returns the line definition in the dat file
        """
        dest = io.StringIO()
        if len(self.fibers) > 0:
            dest.write("FNODE")
        else:
            dest.write("NODE")

        if self.id is None:
            raise RuntimeError("You have to compute ids before writing")

        dest.write(
            " {0} COORD {1}".format(self.id, " ".join([repr(i) for i in self.coords]))
        )

        for k, f in self.fibers.items():
            dest.write(" ")
            f.write(dest, k)

        return dest.getvalue()

    def write(self, dest):
        """
        Writes the corresponding line in to the stream variable

        Args:
            dest: stream variable where to write the line
        """
        if len(self.fibers) > 0:
            dest.write("FNODE")
        else:
            dest.write("NODE")

        if self.id is None:
            raise RuntimeError("You have to compute ids before writing")

        dest.write(
            " {0} COORD {1}".format(self.id, " ".join([repr(i) for i in self.coords]))
        )

        for k, f in self.fibers.items():
            dest.write(" ")
            f.write(dest, k)

        dest.write("\n")
