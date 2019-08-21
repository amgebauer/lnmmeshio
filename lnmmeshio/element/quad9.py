from .element import Element2D
from ..node import Node
from typing import List, Dict
from .line3 import Line3
import numpy as np

"""
Implementation of a quad9 element
"""
class Quad9 (Element2D):
    ShapeName: str = 'QUAD9'

    """
    Base constructor of a Quad9 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Quad9, self).__init__(el_type, Quad9.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a QUAD9 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a QUAD9 element

    Returns:
        Number of nodes of a QUAD9 element = 9
    """
    def get_num_nodes(self) -> int:
        return 9
    
    """
    The face of a quad9 element is itself

    Returns:
        List of faces
    """
    def get_faces(self) -> List['Quad9']:
        return [self]
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List[Line3]:
        return [
            Line3(None, [self.nodes[0], self.nodes[1], self.nodes[4]]),
            Line3(None, [self.nodes[1], self.nodes[2], self.nodes[5]]),
            Line3(None, [self.nodes[2], self.nodes[3], self.nodes[6]]),
            Line3(None, [self.nodes[3], self.nodes[0], self.nodes[7]])
        ]
    
    """
    Returns the value of the shape functions at the local coordinate xi
    """
    @staticmethod
    def shape_fcns(xi):

        return np.array(
            [Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[1],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[1],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[2],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[1],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[2],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[2]])