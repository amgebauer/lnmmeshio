from .element import Element2D
from ..node import Node
from typing import List, Dict
from .line2 import Line2
import numpy as np

"""
Implementation of a quad4 element
"""


class Quad4(Element2D):
    ShapeName: str = "QUAD4"

    """
    Base constructor of a Quad4 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Quad4, self).__init__(el_type, Quad4.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a QUAD4 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a QUAD4 element

    Returns:
        Number of nodes of a QUAD4 element = 4
    """

    def get_num_nodes(self) -> int:
        return 4

    """
    The face of a quad4 element is itself

    Returns:
        List of faces
    """

    def get_faces(self) -> List["Quad4"]:
        return [self]

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List[Line2]:
        return [
            Line2(None, [self.nodes[0], self.nodes[1]]),
            Line2(None, [self.nodes[1], self.nodes[2]]),
            Line2(None, [self.nodes[2], self.nodes[3]]),
            Line2(None, [self.nodes[3], self.nodes[0]]),
        ]

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):

        return np.array(
            [
                Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns(xi[1])[0],
                Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns(xi[1])[0],
                Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns(xi[1])[1],
                Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns(xi[1])[1],
            ]
        )
