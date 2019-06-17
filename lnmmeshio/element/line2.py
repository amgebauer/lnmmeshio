from .element import Element
from ..node import Node
from typing import List, Dict

"""
Implementation of a line2 element
"""
class Line2 (Element):
    ShapeName: str = 'LINE2'

    """
    Base constructor of a line2 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Line2, self).__init__(el_type, Line2.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a LINE2 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a LINE2 element

    Returns:
        Number of nodes of a line2 element = 2
    """
    def get_num_nodes(self) -> int:
        return 2
    
    """
    A LINE2 element does not contain any faces

    Returns:
        List of faces
    """
    def get_faces(self) -> List['Line2']:
        return []
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List['Line2']:
        return [self]