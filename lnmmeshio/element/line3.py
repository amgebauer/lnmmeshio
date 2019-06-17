from .element import Element
from ..node import Node
from typing import List, Dict

"""
Implementation of a line3 element
"""
class Line3 (Element):
    ShapeName: str = 'LINE3'

    """
    Base constructor of a line3 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Line3, self).__init__(el_type, Line3.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a LINE3 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a LINE3 element

    Returns:
        Number of nodes of a line3 element = 3
    """
    def get_num_nodes(self) -> int:
        return 3
    
    """
    A LINE3 element does not contain any faces

    Returns:
        List of faces
    """
    def get_faces(self) -> List:
        return []
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List['Line3']:
        return [self]