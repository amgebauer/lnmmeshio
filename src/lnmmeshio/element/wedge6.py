from typing import List

import numpy as np
from lnmmeshio.element.quad4 import Quad4
from lnmmeshio.element.tri3 import Tri3

from ..node import Node
from .element import Element2D, Element3D


class Wedge6(Element3D):
    """
    Implementation of a WEDGE6 element
    """

    ShapeName: str = "WEDGE6"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Wedge6 element
        """
        super(Wedge6, self).__init__(el_type, Wedge6.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a WEDGE6 element with {0} nodes".format(
                    len(nodes)
                )
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a WEDGE6 element

        Returns:
            Number of nodes of a Wedge6 element = 6
        """
        return 6

    def get_faces(self) -> List[Element2D]:
        """
        Returns a list of faces of the Wedge6 element

        Returns:
            List of faces
        """
        face_node_ids = [[0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5], [0, 1, 2], [3, 4, 5]]

        def gen_face(nodes):
            if len(nodes) == 3:
                return Tri3(None, nodes)
            else:
                return Quad4(None, nodes)

        return [gen_face([self.nodes[i] for i in nodes]) for nodes in face_node_ids]
