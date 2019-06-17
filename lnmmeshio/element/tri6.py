from .element import Element
from ..node import Node
from typing import List, Dict
from .line3 import Line3

"""
Implementation of a tri6 element
"""
class Tri6 (Element):
    ShapeName: str = 'TRI6'

    """
    Base constructor of a tri6 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Tri6, self).__init__(el_type, Tri6.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a TRI6 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a TRI6 element

    Returns:
        Number of nodes of a TRI6 element = 6
    """
    def get_num_nodes(self) -> int:
        return 6
    
    """
    A TRI6 element does not contain any faces

    Returns:
        List of faces
    """
    def get_faces(self) -> List['Tri6']:
        return [self]
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List[Line3]:
        return [
            Line3(None, [self.nodes[0], self.nodes[1], self.nodes[3]]),
            Line3(None, [self.nodes[1], self.nodes[2], self.nodes[4]]),
            Line3(None, [self.nodes[2], self.nodes[0], self.nodes[5]])
        ]