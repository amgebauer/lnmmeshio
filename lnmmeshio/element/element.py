from typing import List
import numpy as np
import io
from ..ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value, line_option_list
from collections import OrderedDict
from ..node import Node


"""
Class holding the data of one element
"""
class Element:

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
    Returns a list of nodes

    Returns:
        List of nodes
    """
    def get_nodes(self) -> List[Node]:
        return self.nodes

    """
    Returns all faces

    Returns:
        List of faces
    """
    def get_faces(self) -> list:
        raise RuntimeError("This element does't implement get faces")

    """
    Returns all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> list:
        raise RuntimeError("This element does't implement get edges")

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
    Returns a list of dpoints that is shared by all nodes of the element

    Returns:
        List of dpoint
    """
    def get_dpoints(self):
        pointnodesets = None

        for p in self.nodes:
            if pointnodesets is None:
                pointnodesets = set(p.pointnodesets)
            else:
                pointnodesets = set(p.pointnodesets).intersection(pointnodesets)
        
        return list(pointnodesets)

    """
    Returns a list of dlines that is shared by all nodes of the element

    Returns:
        List of dlines
    """
    def get_dlines(self):
        linenodesets = None

        for p in self.nodes:
            if linenodesets is None:
                linenodesets = set(p.linenodesets)
            else:
                linenodesets = set(p.linenodesets).intersection(linenodesets)
        
        return list(linenodesets)

    """
    Returns a list of dsurf that is shared by all nodes of the element

    Returns:
        List of dsurfs
    """
    def get_dsurfs(self):
        surfacenodesets = None

        for p in self.nodes:
            if surfacenodesets is None:
                surfacenodesets = set(p.surfacenodesets)
            else:
                surfacenodesets = set(p.surfacenodesets).intersection(surfacenodesets)
        
        return list(surfacenodesets)

    """
    Returns a list of dvol that is shared by all nodes of the element

    Returns:
        List of dvols
    """
    def get_dvols(self):
        volumenodesets = None

        for p in self.nodes:
            if volumenodesets is None:
                volumenodesets = set(p.volumenodesets)
            else:
                volumenodesets = set(p.volumenodesets).intersection(volumenodesets)
        
        return list(volumenodesets)

    def get_line(self):
        line = io.StringIO()
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        line.write('{0} {1} '.format(self.id, self.type))

        options: OrderedDict = OrderedDict()
        options[self.shape] = [i.id for i in self.nodes]
        options.update(self.options)

        line.write(line_option_list(options))

        for t, f in self.fibers.items():
            line.write(' ')
            line.write(f.get_line(t))
        
        return line.getvalue()

    
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
    Returns the number of nodes from the shapes

    Args:
        shape: shape as used in baci .dat file format
    
    Returngs:
        int: number of nodes
    """
    @staticmethod
    def num_nodes_by_shape(shape: str):
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
            "TRI6"    : 6,
            "LINE2"   : 2,
            "LINE3"   : 3,
            "QUAD8"   : 8,
            "QUAD9"   : 9,
        }
        
        if shape not in shape_dict:
            raise ValueError('Element of shape {0} is unknown'.format(shape))
        
        return shape_dict[shape]