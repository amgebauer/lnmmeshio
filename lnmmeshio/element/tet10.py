import math
from typing import List

import numpy as np

from ..node import Node
from .element import ElementTet
from .line3 import Line3
from .tri6 import Tri6


"""
Implementation of a tet4 element
"""


class Tet10(ElementTet):
    ShapeName: str = "TET10"

    """
    Base constructor of a tet10 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Tet10, self).__init__(el_type, Tet10.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TET10 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a TET10 element

        Returns:
            Number of nodes of a TET10 element = 10
        """
        return 10

    """
    Returns a list of faces of the TET10 element

    Returns:
        List of faces
    """

    def get_faces(self) -> List[Tri6]:
        face_node_ids = [
            [0, 1, 3, 4, 8, 7],
            [1, 2, 3, 5, 9, 8],
            [2, 0, 3, 6, 7, 9],
            [0, 2, 1, 6, 5, 4],
        ]

        return [Tri6(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids]

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List[Line3]:
        edge_node_ids = [
            [0, 1, 4],
            [1, 2, 5],
            [2, 0, 6],
            [0, 3, 7],
            [1, 3, 8],
            [2, 3, 9],
        ]
        return [Line3(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids]

    def get_xi(self, x):
        """
        Returns the local variables from given global variables

        Args:
            x: Global variable

        Returns:
            Local variables (xi)
        """
        coords = np.transpose(np.array([n.coords for n in self.nodes]))
        raise NotImplementedError("This is currently not implemented for all elements")

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        r = xi[0]
        s = xi[1]
        t = xi[2]
        u = 1.0 - r - s - t
        return np.array(
            [
                u * (2.0 * u - 1.0),
                r * (2.0 * r - 1.0),
                s * (2.0 * s - 1.0),
                t * (2.0 * t - 1.0),
                4.0 * r * u,
                4.0 * r * s,
                4.0 * s * u,
                4.0 * t * u,
                4.0 * r * t,
                4.0 * s * t,
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
        u = 1 - xi[0] - xi[1] - xi[2]
        return np.array(
            [
                [
                    -4 * u + 1,
                    4 * xi[0] - 1,
                    0,
                    0,
                    4 * (u - xi[0]),
                    4 * xi[1],
                    -4 * xi[1],
                    -4 * xi[2],
                    4 * xi[2],
                    0,
                ],
                [
                    -4 * u + 1,
                    0,
                    4 * xi[1] - 1,
                    0,
                    -4 * xi[0],
                    4 * xi[0],
                    4 * (u - xi[1]),
                    -4 * xi[2],
                    0,
                    4 * xi[2],
                ],
                [
                    -4 * u + 1,
                    0,
                    0,
                    4 * xi[2] - 1,
                    -4 * xi[0],
                    0,
                    -4 * xi[1],
                    4 * (u - xi[2]),
                    4 * xi[0],
                    4 * xi[1],
                ],
            ]
        )

    @staticmethod
    def nodal_reference_coordinates():
        return np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.0, 0.0],
                [0.5, 0.5, 0.0],
                [0.0, 0.5, 0.0],
                [0.0, 0.0, 0.5],
                [0.5, 0.0, 0.5],
                [0.0, 0.5, 0.5],
            ]
        )
