from .element import Element
from ..node import Node
from typing import List, Dict
from .tri6 import Tri6
from .line3 import Line3

"""
Implementation of a tet4 element
"""
class Tet10 (Element):
    ShapeName: str = 'TET10'

    """
    Base constructor of a tet10 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Tet10, self).__init__(el_type, Tet10.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a TET10 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a TET10 element

    Returns:
        Number of nodes of a TET10 element = 4
    """
    def get_num_nodes(self) -> int:
        return 10
    
    """
    Returns a list of faces of the TET10 element

    Returns:
        List of faces
    """
    def get_faces(self) -> List[Tri6]:
        face_node_ids = [[0, 1, 3, 4, 8, 7], [1, 2, 3, 5, 9, 8], [2, 0, 3, 6, 7, 9], [0, 2, 1, 6, 5, 4]]

        return [
            Tri6(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids
        ]
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List[Line3]:
        edge_node_ids = [[0, 1, 4], [1, 2, 5], [2, 0, 6], [0, 3, 7], [1, 3, 8], [2, 3, 9]]
        return [
            Line3(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids
        ]