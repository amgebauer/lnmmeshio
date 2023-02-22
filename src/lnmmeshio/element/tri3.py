import math
from typing import List

import numpy as np

from ..node import Node
from .element import ElementTri
from .line2 import Line2


class Tri3(ElementTri):
    """
    Implementation of a tri3 element
    """

    ShapeName: str = "TRI3"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a tri3 element
        """
        super(Tri3, self).__init__(el_type, Tri3.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TRI3 element with {0} nodes".format(len(nodes))
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a TRI3 element

        Returns:
            Number of nodes of a TRI3 element = 2
        """
        return 3

    def get_faces(self) -> List["Tri3"]:
        """
        A TRI3 element does not contain any faces

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
            Line2(None, [self.nodes[2], self.nodes[0]]),
        ]

    def integrate_xi(self, integrand, numgp) -> np.ndarray:
        """
        Integrates the integrand over the element

        Args:
            integrand: integrand as a function of xi
            numgp: Number of integration points to be used
        """
        result = np.array(0.0 * integrand(np.zeros((3))))

        intpoints: np.ndarray = ElementTri.int_points(numgp)
        intweights: np.ndarray = ElementTri.int_weights(numgp)

        coords = np.array([n.coords for n in self.nodes])

        for xi, w in zip(intpoints, intweights):
            J = np.matmul(Tri3.shape_fcns_derivs(xi), coords)

            # covariant metric tensor
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
        result = np.array(0.0 * integrand(np.zeros((3))))

        intpoints: np.ndarray = ElementTri.int_points(numgp)
        intweights: np.ndarray = ElementTri.int_weights(numgp)

        coords = np.array([n.coords for n in self.nodes])

        for xi, w in zip(intpoints, intweights):
            x = np.matmul(Tri3.shape_fcns(xi), coords)
            J = np.matmul(Tri3.shape_fcns_derivs(xi), coords)

            # covariant metric tensor
            G = np.matmul(J, J.T)
            detA = math.sqrt(np.linalg.det(G))
            result += w * detA * integrand(x)

        return result

    def get_normal(self, xi):
        u = self.nodes[1].coords - self.nodes[0].coords
        v = self.nodes[2].coords - self.nodes[0].coords
        n = np.cross(u, v)
        return n / np.linalg.norm(n)

    @staticmethod
    def shape_fcns(xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        return np.array([1 - xi[0] - xi[1], xi[0], xi[1]])

    @staticmethod
    def shape_fcns_derivs(xi):
        """
        Returns the value of the derivatives of the shape functions with respect to the local coordinates at the local coordinate xi

        +-                                  -+
        |  dN_1 / dxi_1   dN_2 / dxi_1, ...  |
        |  dN_1 / dxi_2   dN_2 / dxi_2, ...  |
        +-                                  -+
        """
        return np.array([[-1.0, 1.0, 0.0], [-1.0, 0.0, 1.0]])
