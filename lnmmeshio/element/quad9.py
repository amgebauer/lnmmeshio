from typing import List

import numpy as np

from ..node import Node
from .element import ElementQuad
from .line3 import Line3


class Quad9(ElementQuad):
    """
    Implementation of a quad9 element
    """

    ShapeName: str = "QUAD9"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Quad9 element
        """
        super(Quad9, self).__init__(el_type, Quad9.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a QUAD9 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a QUAD9 element

        Returns:
            Number of nodes of a QUAD9 element = 9
        """
        return 9

    def get_faces(self) -> List["Quad9"]:
        """
        The face of a quad9 element is itself

        Returns:
            List of faces
        """
        return [self]

    def get_edges(self) -> List[Line3]:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
        return [
            Line3(None, [self.nodes[0], self.nodes[1], self.nodes[4]]),
            Line3(None, [self.nodes[1], self.nodes[2], self.nodes[5]]),
            Line3(None, [self.nodes[2], self.nodes[3], self.nodes[6]]),
            Line3(None, [self.nodes[3], self.nodes[0], self.nodes[7]]),
        ]

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """

        return np.array(
            [
                Line3.shape_fcns(xi[0])[0] * Line3.shape_fcns(xi[1])[0],
                Line3.shape_fcns(xi[0])[1] * Line3.shape_fcns(xi[1])[0],
                Line3.shape_fcns(xi[0])[1] * Line3.shape_fcns(xi[1])[1],
                Line3.shape_fcns(xi[0])[0] * Line3.shape_fcns(xi[1])[1],
                Line3.shape_fcns(xi[0])[2] * Line3.shape_fcns(xi[1])[0],
                Line3.shape_fcns(xi[0])[1] * Line3.shape_fcns(xi[1])[2],
                Line3.shape_fcns(xi[0])[2] * Line3.shape_fcns(xi[1])[1],
                Line3.shape_fcns(xi[0])[0] * Line3.shape_fcns(xi[1])[2],
                Line3.shape_fcns(xi[0])[2] * Line3.shape_fcns(xi[1])[2],
            ]
        )
