from typing import List

import numpy as np

from ..node import Node
from .element import Element2D
from .line2 import Line2


class Quad4(Element2D):
    """
    Implementation of a quad4 element
    """

    ShapeName: str = "QUAD4"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Quad4 element
        """
        super(Quad4, self).__init__(el_type, Quad4.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a QUAD4 element with {0} nodes".format(len(nodes))
            )

    def get_num_nodes(self) -> int:
        """
        Get number of nodes of a QUAD4 element

        Returns:
            Number of nodes of a QUAD4 element = 4
        """
        return 4

    def get_faces(self) -> List["Quad4"]:
        """
        The face of a quad4 element is itself

        Returns:
            List of faces
        """
        return [self]

    def get_edges(self) -> List[Line2]:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
        return [
            Line2(None, [self.nodes[0], self.nodes[1]]),
            Line2(None, [self.nodes[1], self.nodes[2]]),
            Line2(None, [self.nodes[2], self.nodes[3]]),
            Line2(None, [self.nodes[3], self.nodes[0]]),
        ]

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """

        return np.array(
            [
                Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns(xi[1])[0],
                Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns(xi[1])[0],
                Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns(xi[1])[1],
                Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns(xi[1])[1],
            ]
        )
