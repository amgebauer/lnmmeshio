from typing import List

import numpy as np

from ..node import Node
from .element import ElementHex
from .line2 import Line2
from .quad4 import Quad4


class Hex8(ElementHex):
    """
    Implementation of a HEX8 element
    """

    ShapeName: str = "HEX8"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Hex8 element
        """
        super(Hex8, self).__init__(el_type, Hex8.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a HEX8 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a HEX8 element

        Returns:
            Number of nodes of a Hex8 element = 8
        """
        return 8

    def get_faces(self) -> List[Quad4]:
        """
        Returns a list of faces of the Hex8 element

        Returns:
            List of faces
        """
        face_node_ids = [
            [0, 1, 2, 3],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
        ]

        return [Quad4(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids]

    def get_edges(self) -> List[Line2]:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
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

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """

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

    @staticmethod
    def shape_fcns_derivs(xi):
        """
        Returns the value of the derivatives of the shape functions with respect to the local coordinates at the local coordinate xi

        +-                                  -+
        |  dN_1 / dxi_1   dN_2 / dxi_1, ...  |
        |  dN_1 / dxi_2   dN_2 / dxi_2, ...  |
        |  dN_1 / dxi_3   dN_2 / dxi_3, ...  |
        +-                                  -+
        """

        return np.array(
            [
                [
                    0.125 * (-1 + xi[1] + xi[2] - xi[1] * xi[2]),
                    0.125 * (+1 - xi[1] - xi[2] + xi[1] * xi[2]),
                    0.125 * (+1 + xi[1] - xi[2] - xi[1] * xi[2]),
                    0.125 * (-1 - xi[1] + xi[2] + xi[1] * xi[2]),
                    0.125 * (-1 + xi[1] - xi[2] + xi[1] * xi[2]),
                    0.125 * (+1 - xi[1] + xi[2] - xi[1] * xi[2]),
                    0.125 * (+1 + xi[1] + xi[2] + xi[1] * xi[2]),
                    0.125 * (-1 - xi[1] - xi[2] - xi[1] * xi[2]),
                ],
                [
                    0.125 * (-1 + xi[0] + xi[2] - xi[0] * xi[2]),
                    0.125 * (-1 - xi[0] + xi[2] + xi[0] * xi[2]),
                    0.125 * (+1 + xi[0] - xi[2] - xi[0] * xi[2]),
                    0.125 * (+1 - xi[0] - xi[2] + xi[0] * xi[2]),
                    0.125 * (-1 + xi[0] - xi[2] + xi[0] * xi[2]),
                    0.125 * (-1 - xi[0] - xi[2] - xi[0] * xi[2]),
                    0.125 * (+1 + xi[0] + xi[2] + xi[0] * xi[2]),
                    0.125 * (+1 - xi[0] + xi[2] - xi[0] * xi[2]),
                ],
                [
                    0.125 * (-1 + xi[1] + xi[0] - xi[0] * xi[1]),
                    0.125 * (-1 + xi[1] - xi[0] + xi[0] * xi[1]),
                    0.125 * (-1 - xi[1] - xi[0] - xi[0] * xi[1]),
                    0.125 * (-1 - xi[1] + xi[0] + xi[0] * xi[1]),
                    0.125 * (+1 - xi[1] - xi[0] + xi[0] * xi[1]),
                    0.125 * (+1 - xi[1] + xi[0] - xi[0] * xi[1]),
                    0.125 * (+1 + xi[1] + xi[0] + xi[0] * xi[1]),
                    0.125 * (+1 + xi[1] - xi[0] - xi[0] * xi[1]),
                ],
            ]
        )

    @staticmethod
    def nodal_reference_coordinates():
        return np.array(
            [
                [-1.0, -1.0, -1.0],
                [1.0, -1.0, -1.0],
                [1.0, 1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0],
                [1.0, -1.0, 1.0],
                [1.0, 1.0, 1.0],
                [-1.0, 1.0, 1.0],
            ]
        )
