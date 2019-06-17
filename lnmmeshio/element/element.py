from typing import List
import numpy as np
from ..ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from collections import OrderedDict
from ..node import Node

"""
Class holding the data of one element
"""
class Element:

    ElementEdges: dict = {
        'HEX8': [[0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4]],
        'TET4': [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]],
        'TET10': [[0, 1, 4], [1, 2, 5], [2, 0, 6], [0, 3, 7], [1, 3, 8], [2, 3, 9]]
        # TODO: Need to add more here if necessary
    }
    ElementFaces: dict = {
        'HEX8': [[0, 1, 2, 3], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]],
        'TET4': [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]],
        'TET10': [[0, 1, 3, 4, 8, 7], [1, 2, 3, 5, 9, 8], [2, 0, 3, 6, 7, 9], [0, 2, 1, 6, 5, 4]],
        'TRI3': []
    }

    """
    Creates a new element of type ele_type, shape with nodes defined in nodes

    Args:
        el_type: str of element type as used by BACI (e.g. SOHEX8)
        shape: shape of the element as used by BACI (e.g. HEX8)
        nodes: List of node objects
    """
    def __init__(self, el_type: str, shape: str, nodes: List[Node],
            options: OrderedDict = None):
        self.id = None
        self.type = el_type
        self.shape = shape
        self.nodes = nodes
        self.options = options if options is not None else OrderedDict()
        self.fibers = {}
        self.data = {}
    
    """
    Sets the element id to None
    """
    def reset(self):
        self.id = None
    
    """
    Returns the node ids as of each element as a numpy array of shape (num_ele, num_nod_per_ele)

    Returns:
        np.array with node ids of each element
    """
    def get_node_ids(self):
        arr: np.array = np.zeros((len(self.nodes)), dtype=int)

        for i, node in enumerate(self.nodes, start=0):
            if node.id is None:
                raise RuntimeError('You need to compute ids first')
            arr[i] = node.id
        
        return arr

    
    """
    Write the corresponding element line in the dat file
    """
    def write(self, dest):
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        dest.write('{0} {1} '.format(self.id, self.type))

        options: OrderedDict = OrderedDict()
        options[self.shape] = [i.id for i in self.nodes]
        options.update(self.options)

        write_option_list(dest, options, newline=False)

        for t, f in self.fibers.items():
            dest.write(' ')
            f.write(dest, t)

        dest.write('\n')

    """
    Returns a list of the Faces of the element (The faces are a list of nodes)

    Returns:
        List[List[Node]] List of faces in baci order
    """
    def get_faces(self):
        flist = []

        if self.shape not in self.ElementFaces:
            raise('This element is not implemented')

        for f in self.ElementFaces[self.shape]:
            flist.append([self.nodes[i] for i in f])

        return flist

    """
    Returns the number of nodes from the shapes

    Args:
        shape: shape as used in baci .dat file format
    
    Returngs:
        int: number of nodes
    """
    @staticmethod
    def get_num_nodes(shape: str):
        shape_dict = {
            "TET4"    : 4,
            "TET10"   : 10,
            "PYRAMID5": 5,
            "HEX8"    : 8,
            "HEX20"   : 20,
            "HEX27"   : 27,
            "WEDGE6"  : 6,
            "QUAD4"   : 4,
            "TRI3"    : 3,
            "LINE2"   : 2,
            "QUAD9"   : 9,
        }
        
        if shape not in shape_dict:
            raise ValueError('Element of shape {0} is unknown'.format(shape))
        
        return shape_dict[shape]