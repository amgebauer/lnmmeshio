from typing import List

import numpy as np

from ..node import Node
from .element import Element1D

"""
Implementation of a line3 element
"""


class Line3(Element1D):
    ShapeName: str = "LINE3"

    """
    Base constructor of a line3 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Line3, self).__init__(el_type, Line3.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a LINE3 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a LINE3 element

    Returns:
        Number of nodes of a line3 element = 3
    """

    def get_num_nodes(self) -> int:
        return 3

    """
    A LINE3 element does not contain any faces

    Returns:
        List of faces
    """

    def get_faces(self) -> List:
        return []

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List["Line3"]:
        return [self]

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):
        return np.array([xi * (xi - 1) / 2.0, xi * (xi + 1) / 2.0, (1 + xi) * (1 - xi)])
