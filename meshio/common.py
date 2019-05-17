# -*- coding: utf-8 -*-

import numpy as np

def get_etype(baci):
    # map element names: baci -> meshio
    ele_dic = {'PYRAMID5':'pyramid',
               'TET4':'tetra',
               'HEX8':'hexahedron',
               'WEDGE6':'wedge',
               'QUAD4':'quad',
               'TET10':'tetra10',
               'HEX20':'hexahedron',
               'QUAD9':'quad',
               'LINE2':'line',
               'HEX27':'hexahedron',
               'TRI3':'triangle'}
    
    try:
        etype = ele_dic[baci]
    except KeyError:
        RuntimeError('Element type ' + baci + ' not yet implemented.')
    
    return etype

# dict node:surface, e.g.
# {1: 1,
#  ...
#  15746: 3}
#
# ATTENTION: one node might belong to several surfaces!
# here, only the surface with the SMALLEST ID is stored
def flip_map(surface_node_map):
    # max node number
    n_max = max([s.max() for s in surface_node_map.values()])
    
    # loop surfaces
    node_surface_map = np.zeros(n_max+1, int)
    for surf in reversed(sorted(surface_node_map.keys())):
        # loop nodes of current surface
        for node in surface_node_map[surf]:
                node_surface_map[node] = surf
    return node_surface_map

class MeshObject:
    def __init__(self):
        # [coordinates]
        self._points = []
        
        # cell-type: [node IDs]
        self._cells = {}
        
        # name:[values for all nodes]
        self._point_data = {}
        
        # name:[values for all elements]
        self._cell_data = {}
        
        # dict surface:nodes
        self._surface_node_map = {}
        
        # dict node:surface (with smallest ID)
        # mesh._node_surface_map = {}
        
        # not sure what this is...
        self._field_data = {}
        
        return

