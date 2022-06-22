import math
from typing import List

import numpy as np

from ..node import Node
from .element import ElementQuad
from .line2 import Line2


class Quad4(ElementQuad):
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

    @classmethod
    def get_num_nodes(cls) -> int:
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

    @staticmethod
    def shape_fcns_derivs(xi):
        """
        Returns the value of the derivatives of the shape functions with respect to the local coordinates at the local coordinate xi

        +-                                  -+
        |  dN_1 / dxi_1   dN_2 / dxi_1, ...  |
        |  dN_1 / dxi_2   dN_2 / dxi_2, ...  |
        +-                                  -+
        """

        return np.array(
            [
                [
                    Line2.shape_fcns_derivs(xi[0])[0] * Line2.shape_fcns(xi[1])[0],
                    Line2.shape_fcns_derivs(xi[0])[1] * Line2.shape_fcns(xi[1])[0],
                    Line2.shape_fcns_derivs(xi[0])[1] * Line2.shape_fcns(xi[1])[1],
                    Line2.shape_fcns_derivs(xi[0])[0] * Line2.shape_fcns(xi[1])[1],
                ],
                [
                    Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns_derivs(xi[1])[0],
                    Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns_derivs(xi[1])[0],
                    Line2.shape_fcns(xi[0])[1] * Line2.shape_fcns_derivs(xi[1])[1],
                    Line2.shape_fcns(xi[0])[0] * Line2.shape_fcns_derivs(xi[1])[1],
                ],
            ]
        )

    def integrate_xi(self, integrand, numgp) -> np.ndarray:
        """
        Integrates the integrand over the element

        Args:
            integrand: integrand as a function of xi
            numgp: Number of integration points to be used
        """
        result = np.array(0.0 * integrand(np.zeros((3))))

        intpoints: np.ndarray = ElementQuad.int_points(numgp)
        intweights: np.ndarray = ElementQuad.int_weights(numgp)

        coords = np.array([n.coords for n in self.nodes])

        for xi, w in zip(intpoints, intweights):
            J = np.matmul(Quad4.shape_fcns_derivs(xi), coords)

            # covariant metric tensor
            G = np.matmul(J, J.T)
            detA = math.sqrt(np.linalg.det(G))
            result += w * detA * integrand(xi)

        return result

    def get_normal(self, xi):
        """
        This is just an approximation assuming that the surface is plane
        """
        u = self.nodes[1].coords - self.nodes[0].coords
        v = self.nodes[2].coords - self.nodes[0].coords
        n = np.cross(u, v)
        return n / np.linalg.norm(n)
