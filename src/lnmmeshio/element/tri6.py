import math
from typing import List

import numpy as np

from ..node import Node
from .element import ElementTri
from .line3 import Line3


class Tri6(ElementTri):
    """
    Implementation of a tri6 element
    """

    ShapeName: str = "TRI6"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a tri6 element
        """
        super(Tri6, self).__init__(el_type, Tri6.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TRI6 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a TRI6 element

        Returns:
            Number of nodes of a TRI6 element = 6
        """
        return 6

    def get_faces(self) -> List["Tri6"]:
        """
        A TRI6 element does not contain any faces

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
            Line3(None, [self.nodes[0], self.nodes[1], self.nodes[3]]),
            Line3(None, [self.nodes[1], self.nodes[2], self.nodes[4]]),
            Line3(None, [self.nodes[2], self.nodes[0], self.nodes[5]]),
        ]

    def integrate_xi(self, integrand, numgp) -> np.ndarray:
        """
        Integrates the integrand over the element

        Args:
            integrand: integrand as a function of xi
            numgp: Number of integration points to be used
        """
        result = np.array(0.0)

        intpoints: np.ndarray = ElementTri.int_points(numgp)
        intweights: np.ndarray = ElementTri.int_weights(numgp)

        coords = np.array([n.coords for n in self.nodes])

        for xi, w in zip(intpoints, intweights):
            J = np.matmul(Tri6.shape_fcns_derivs(xi), coords)
            G = np.matmul(J, J.T)
            detA = math.sqrt(np.linalg.det(G))
            result += w * detA * integrand(xi)

        return result

    def integrate(self, integrand, numgp) -> np.ndarray:
        """
        Integrates the integrand over the element

        Args:
            integrand: integrand as a function of x
            numgp: Number of integration points to be used
        """
        result = np.array(0.0)

        intpoints: np.ndarray = ElementTri.int_points(numgp)
        intweights: np.ndarray = ElementTri.int_weights(numgp)

        coords = np.array([n.coords for n in self.nodes])

        for xi, w in zip(intpoints, intweights):
            x = np.matmul(Tri6.shape_fcns(xi), coords)
            J = np.matmul(Tri6.shape_fcns_derivs(xi), coords)
            G = np.matmul(J, J.T)
            detA = math.sqrt(np.linalg.det(G))
            result += w * detA * integrand(x)

        return result

    def get_normal(self, xi):
        coords = np.array([n.coords for n in self.nodes])
        J = np.matmul(Tri6.shape_fcns_derivs(xi), coords)

        n = np.cross(J[0, :], J[1, :])
        return n / np.linalg.norm(n)

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        r = xi[0]
        s = xi[1]

        t1 = 1.0 - r - s
        t2 = r
        t3 = s

        return np.array(
            [
                t1 * (2.0 * t1 - 1.0),
                t2 * (2.0 * t2 - 1.0),
                t3 * (2.0 * t3 - 1.0),
                4.0 * t2 * t1,
                4.0 * t2 * t3,
                4.0 * t3 * t1,
            ]
        )

    @staticmethod
    def shape_fcns_derivs(xi):
        """
        Returns the value of the derivatives of the shape functions with respect to the local coordinates at the local coordinate xi

        +-                                  -+
        |  dN_1 / dxi_1   dN_2 / dxi_1, ...  |
        |  dN_1 / dxi_2   dN_2 / dxi_2, ...  |
        +-                                  -+
        """
        t1 = 1.0 - xi[0] - xi[1]
        t2 = xi[0]
        t3 = xi[1]

        return np.array(
            [
                [
                    -(4.0 * t1 - 1),
                    4.0 * t2 - 1,
                    0.0,
                    4.0 * t1 - 4.0 * t2,
                    4.0 * t3,
                    -4.0 * t3,
                ],
                [
                    -(4.0 * t1 - 1),
                    0.0,
                    4.0 * t3 - 1,
                    -4.0 * t2,
                    4 * t2,
                    4.0 * t1 - 4.0 * t3,
                ],
            ]
        )
