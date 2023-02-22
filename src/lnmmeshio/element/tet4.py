from typing import List

import numpy as np

from ..node import Node
from .element import ElementTet
from .line2 import Line2
from .tri3 import Tri3


class Tet4(ElementTet):
    """
    Implementation of a tet4 element
    """

    ShapeName: str = "TET4"
    ShapeFunctionsN: np.ndarray = np.array(
        [[-1.0, -1.0, -1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    ShapeFunctionsB: np.ndarray = np.array([1.0, 0.0, 0.0, 0.0])
    NodalReferenceCoordinates: np.ndarray = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a tet4 element
        """
        super(Tet4, self).__init__(el_type, Tet4.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TET4 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a TET4 element

        Returns:
            Number of nodes of a tet4 element = 4
        """
        return 4

    def get_faces(self) -> List[Tri3]:
        """
        Returns a list of faces of the tet4 element

        Returns:
            List of faces
        """
        face_node_ids = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]

        return [Tri3(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids]

    def get_edges(self) -> List[Line2]:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
        edge_node_ids = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]]
        return [Line2(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids]

    def get_xi(self, x):
        coords = np.transpose(np.array([n.coords for n in self.nodes]))
        N, b = Tet4.shape_fcns_mv()

        return np.linalg.solve(np.dot(coords, N), x - np.dot(coords, b))

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        N, b = Tet4.shape_fcns_mv()
        if len(xi.shape) == 2:
            b = b.reshape((4, 1))
        return np.matmul(N, xi) + b

    @staticmethod
    def shape_fcns_mv():
        return (
            Tet4.ShapeFunctionsN,
            Tet4.ShapeFunctionsB,
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
                    -1,
                    1,
                    0,
                    0,
                ],
                [-1, 0, 1, 0],
                [
                    -1,
                    0,
                    0,
                    1,
                ],
            ]
        )

    @staticmethod
    def nodal_reference_coordinates():
        return Tet4.NodalReferenceCoordinates
