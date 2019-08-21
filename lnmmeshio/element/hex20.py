from .element import ElementHex
from ..node import Node
from typing import List, Dict
from .quad8 import Quad8
from .line3 import Line3
import numpy as np

"""
Implementation of a HEX20 element
"""
class Hex20 (ElementHex):
    ShapeName: str = 'HEX20'

    """
    Base constructor of a Hex20 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Hex20, self).__init__(el_type, Hex20.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a HEX20 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a HEX20 element

    Returns:
        Number of nodes of a Hex20 element = 20
    """
    def get_num_nodes(self) -> int:
        return 20
    
    """
    Returns a list of faces of the Hex20 element

    Returns:
        List of faces
    """
    def get_faces(self) -> List[Quad8]:
        face_node_ids = [
            [0, 1, 2, 3, 8, 9, 10, 11],
            [0, 1, 5, 4, 8, 13, 16, 12],
            [1, 2, 6, 5, 9, 14, 17, 13],
            [2, 3, 7, 6, 10, 15, 18, 14],
            [3, 0, 4, 7, 11, 12, 19, 15],
            [4, 5, 6, 7, 15, 17, 18, 19]]

        return [
            Quad8(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids
        ]
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List[Line3]:
        edge_node_ids = [
            [0, 1, 8],
            [1, 2, 9],
            [2, 3, 10],
            [3, 0, 11],
            [0, 4, 12],
            [1, 5, 13],
            [2, 6, 14],
            [3, 7, 15],
            [4, 5, 16],
            [5, 6, 17],
            [6, 7, 18],
            [7, 4, 19]]
        return [
            Line3(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids
        ]
    
    """
    Returns the value of the shape functions at the local coordinate xi
    """
    @staticmethod
    def shape_fcns(xi):

        r = xi[0]
        s = xi[1]
        t = xi[2]

        rp = 1.0 + r
        rm = 1.0 - r
        sp = 1.0 + s
        sm = 1.0 - s
        tp = 1.0 + t
        tm = 1.0 - t
        rrm = 1.0 - r * r
        ssm = 1.0 - s * s
        ttm = 1.0 - t * t

        return np.array([
            0.125 * rm * sm * tm * (rm + sm + tm - 5.0),
            0.125 * rp * sm * tm * (rp + sm + tm - 5.0),
            0.125 * rp * sp * tm * (rp + sp + tm - 5.0),
            0.125 * rm * sp * tm * (rm + sp + tm - 5.0),
            0.125 * rm * sm * tp * (rm + sm + tp - 5.0),
            0.125 * rp * sm * tp * (rp + sm + tp - 5.0),
            0.125 * rp * sp * tp * (rp + sp + tp - 5.0),
            0.125 * rm * sp * tp * (rm + sp + tp - 5.0),
            0.25 * rrm * sm * tm,
            0.25 * rp * ssm * tm,
            0.25 * rrm * sp * tm,
            0.25 * rm * ssm * tm,
            0.25 * rm * sm * ttm,
            0.25 * rp * sm * ttm,
            0.25 * rp * sp * ttm,
            0.25 * rm * sp * ttm,
            0.25 * rrm * sm * tp,
            0.25 * rp * ssm * tp,
            0.25 * rrm * sp * tp,
            0.25 * rm * ssm * tp
        ])