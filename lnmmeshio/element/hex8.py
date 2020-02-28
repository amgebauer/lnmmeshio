from typing import List

import numpy as np

from ..node import Node
from .element import ElementHex
from .line2 import Line2
from .quad4 import Quad4


"""
Implementation of a HEX8 element
"""


class Hex8(ElementHex):
    ShapeName: str = "HEX8"

    """
    Base constructor of a Hex8 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Hex8, self).__init__(el_type, Hex8.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a HEX8 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a HEX8 element

    Returns:
        Number of nodes of a Hex8 element = 8
    """

    def get_num_nodes(self) -> int:
        return 8

    """
    Returns a list of faces of the Hex8 element

    Returns:
        List of faces
    """

    def get_faces(self) -> List[Quad4]:
        face_node_ids = [
            [0, 1, 2, 3],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
        ]

        return [Quad4(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids]

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List[Line2]:
        edge_node_ids = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
        ]
        return [Line2(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids]

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):

        return np.array(
            [
                Line2.shape_fcns(xi[0])[0]
                * Line2.shape_fcns(xi[1])[0]
                * Line2.shape_fcns(xi[2])[0],
                Line2.shape_fcns(xi[0])[1]
                * Line2.shape_fcns(xi[1])[0]
                * Line2.shape_fcns(xi[2])[0],
                Line2.shape_fcns(xi[0])[1]
                * Line2.shape_fcns(xi[1])[1]
                * Line2.shape_fcns(xi[2])[0],
                Line2.shape_fcns(xi[0])[0]
                * Line2.shape_fcns(xi[1])[1]
                * Line2.shape_fcns(xi[2])[0],
                Line2.shape_fcns(xi[0])[0]
                * Line2.shape_fcns(xi[1])[0]
                * Line2.shape_fcns(xi[2])[1],
                Line2.shape_fcns(xi[0])[1]
                * Line2.shape_fcns(xi[1])[0]
                * Line2.shape_fcns(xi[2])[1],
                Line2.shape_fcns(xi[0])[1]
                * Line2.shape_fcns(xi[1])[1]
                * Line2.shape_fcns(xi[2])[1],
                Line2.shape_fcns(xi[0])[0]
                * Line2.shape_fcns(xi[1])[1]
                * Line2.shape_fcns(xi[2])[1],
            ]
        )
