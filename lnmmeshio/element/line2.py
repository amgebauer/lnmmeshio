from typing import List

import numpy as np

from ..node import Node
from .element import Element1D


class Line2(Element1D):
    """
    Implementation of a line2 element
    """

    ShapeName: str = "LINE2"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a line2 element
        """
        super(Line2, self).__init__(el_type, Line2.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a LINE2 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a LINE2 element

        Returns:
            Number of nodes of a line2 element = 2
        """
        return 2

    def get_faces(self) -> List["Line2"]:
        """
        A LINE2 element does not contain any faces

        Returns:
            List of faces
        """
        return []

    def get_edges(self) -> List["Line2"]:
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
        return np.array([(1 - xi) / 2.0, (1 + xi) / 2.0])

    @staticmethod
    def shape_fcns_derivs(xi):
        """
        Returns the value of the derivatives of the shape functions with respect to the local coordinates at the local coordinate xi

        +-                             -+
        |  dN_1 / dxi_1   dN_2 / dxi_1  |
        +-                             -+
        """
        return np.array([-0.5, 0.5])
