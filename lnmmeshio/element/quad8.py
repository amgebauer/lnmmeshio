from typing import List

import numpy as np

from ..node import Node
from .element import Element2D
from .line3 import Line3


"""
Implementation of a quad8 element
"""


class Quad8(Element2D):
    ShapeName: str = "QUAD8"

    """
    Base constructor of a Quad8 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Quad8, self).__init__(el_type, Quad8.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a QUAD8 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a QUAD8 element

    Returns:
        Number of nodes of a QUAD8 element = 8
    """

    def get_num_nodes(self) -> int:
        return 8

    """
    The face of a quad8 element is itself

    Returns:
        List of faces
    """

    def get_faces(self) -> List["Quad8"]:
        return [self]

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List[Line3]:
        return [
            Line3(None, [self.nodes[0], self.nodes[1], self.nodes[4]]),
            Line3(None, [self.nodes[1], self.nodes[2], self.nodes[5]]),
            Line3(None, [self.nodes[2], self.nodes[3], self.nodes[6]]),
            Line3(None, [self.nodes[3], self.nodes[0], self.nodes[7]]),
        ]

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):

        r = xi[0]
        s = xi[1]

        rp = 1.0 + r
        rm = 1.0 - r
        sp = 1.0 + s
        sm = 1.0 - s
        r2 = 1.0 - r * r
        s2 = 1.0 - s * s

        return np.array(
            [
                0.25 * (rm * sm - (r2 * sm + s2 * rm)),
                0.25 * (rp * sm - (r2 * sm + s2 * rp)),
                0.25 * (rp * sp - (s2 * rp + r2 * sp)),
                0.25 * (rm * sp - (r2 * sp + s2 * rm)),
                0.5 * r2 * sm,
                0.5 * s2 * rp,
                0.5 * r2 * sp,
                0.5 * s2 * rm,
            ]
        )
