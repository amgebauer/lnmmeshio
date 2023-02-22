from typing import List

from ..node import Node
from .element import Element0D


class Vertex(Element0D):
    """
    Implementation of a Vertex element
    """

    ShapeName: str = "VERTEX1"

    def __init__(self, el_type: str, nodes: List[Node]):
        """
        Base constructor of a Vertex element
        """
        super(Vertex, self).__init__(el_type, Vertex.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError(
                "You tried to created a Vertex element with {0} nodes".format(
                    len(nodes)
                )
            )

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of a VERTEX element

        Returns:
            Number of nodes of a VERTEX element = 1
        """
        return 1

    def get_faces(self) -> List:
        """
        A VERTEX element does not contain any faces

        Returns:
            List of faces
        """
        return []

    def get_edges(self) -> List:
        """
        Returns the list of all edges

        Returns:
            List of edges
        """
        return []
