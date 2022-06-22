from typing import List, Optional

import numpy as np

from ..node import Node
from .element import Element1D


class Line3(Element1D):
    """
    Implementation of a line3 element
    """

    ShapeName: str = "LINE3"

    def __init__(self, el_type: Optional[str], nodes: List[Node]):
        """
        Base constructor of a line3 element
        """
        super(Line3, self).__init__(el_type, Line3.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a LINE3 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a LINE3 element

        Returns:
            Number of nodes of a line3 element = 3
        """
        return 3

    def get_faces(self) -> List:
        """
        A LINE3 element does not contain any faces

        Returns:
            List of faces
        """
        return []

    def get_edges(self) -> List["Line3"]:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
        return [self]

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        return np.array([xi * (xi - 1) / 2.0, xi * (xi + 1) / 2.0, (1 + xi) * (1 - xi)])
