from typing import List

import numpy as np
from lnmmeshio.element.quad4 import Quad4
from lnmmeshio.element.tri3 import Tri3

from ..node import Node
from .element import Element2D, Element3D


class Pyramid5(Element3D):
    """
    Implementation of a PYRAMID5 element
    """

    ShapeName: str = "PYRAMID5"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Pyramid5 element
        """
        super(Pyramid5, self).__init__(el_type, Pyramid5.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a PYRAMID5 element with {0} nodes".format(
                    len(nodes)
                )
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a PYRAMID5 element

        Returns:
            Number of nodes of a PYRAMID5 element = 5
        """
        return 5

    def get_faces(self) -> List[Element2D]:
        """
        Returns a list of faces of the Wedge6 element

        Returns:
            List of faces
        """
        face_node_ids = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]

        def gen_face(nodes):
            if len(nodes) == 3:
                return Tri3(None, nodes)
            else:
                return Quad4(None, nodes)

        return [gen_face([self.nodes[i] for i in nodes]) for nodes in face_node_ids]
