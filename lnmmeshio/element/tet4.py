from .element import ElementTet
from ..node import Node
from typing import List, Dict
from .tri3 import Tri3
from .line2 import Line2
import numpy as np

"""
Implementation of a tet4 element
"""


class Tet4(ElementTet):
    ShapeName: str = "TET4"

    """
    Base constructor of a tet4 element
    """

    def __init__(self, el_type: str, nodes: List[Node]):
        super(Tet4, self).__init__(el_type, Tet4.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a TET4 element with {0} nodes".format(len(nodes))
            )

    """
    Get number of nodes of a TET4 element

    Returns:
        Number of nodes of a tet4 element = 4
    """

    def get_num_nodes(self) -> int:
        return 4

    """
    Returns a list of faces of the tet4 element

    Returns:
        List of faces
    """

    def get_faces(self) -> List[Tri3]:
        face_node_ids = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]

        return [Tri3(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids]

    """
    Returns the list of all edges

    Returns:
        List of edges
    """

    def get_edges(self) -> List[Line2]:
        edge_node_ids = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]]
        return [Line2(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids]

    def get_xi(self, x):
        coords = np.transpose(np.array([n.coords for n in self.nodes]))
        N, b = Tet4.shape_fcns_mv()

        return np.linalg.solve(np.dot(coords, N), x - np.dot(coords, b))

    """
    Returns the value of the shape functions at the local coordinate xi
    """

    @staticmethod
    def shape_fcns(xi):
        N, b = Tet4.shape_fcns_mv()
        return np.dot(N, xi) + b

    @staticmethod
    def shape_fcns_mv():
        return (
            np.array(
                [[-1.0, -1.0, -1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
            ),
            np.array([1.0, 0.0, 0.0, 0.0]),
        )
