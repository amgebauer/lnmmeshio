from .element import Element2D
from ..node import Node
from typing import List, Dict
from .line2 import Line2
import numpy as np

"""
Implementation of a tri3 element
"""


class Tri3(Element2D):
    ShapeName: str = "TRI3"

    """
    Base constructor of a tri3 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Tri3, self).__init__(el_type, Tri3.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TRI3 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a TRI3 element

    Returns:
        Number of nodes of a TRI3 element = 2
    """

    def get_num_nodes(self) -> int:
        return 3

    """
    A TRI3 element does not contain any faces

    Returns:
        List of faces
    """

    def get_faces(self) -> List["Tri3"]:
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
            Line2(None, [self.nodes[2], self.nodes[0]]),
        ]

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):
        return np.array([1 - xi[0] - xi[1], xi[0], xi[1]])
