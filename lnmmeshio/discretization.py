import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from collections import OrderedDict
import re
from .element.element import Element
from .element.element_container import ElementContainer
from .node import Node
from .fiber import Fiber
from .progress import progress

"""
This class holds the discretization, consisting out of nodes and elements. The nodes and
elements itself hold their data (coords, element type, ...)
"""
class Discretization:

    """
    Initialize Discretization class with empty nodes and zero elements
    """
    def __init__(self):
        self.nodes: List[Node] = []
        self.elements: ElementContainer = ElementContainer()
    
    """
    Computes the ids of the elements and nodes. 

    Args:
        zero_based: If true, the first node id is 0, otherwise 1
    """
    def compute_ids(self, zero_based: bool):
        
        id: int = 0 if zero_based else 1
        for node in self.nodes:
            node.id = id
            id += 1
        
        id: int = 0 if zero_based else 1
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.id = id
                id += 1
    
    """
    Resets the computed ids
    """
    def reset(self):
        for node in self.nodes:
            node.reset()
        
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.reset()

    """
    Returns an np.array((num_node, 3)) with the coordinates of each node
    """
    def get_node_coords(self):
        arr: np.array = np.zeros((len(self.nodes), 3))

        i: int = 0
        for node in self.nodes:
            arr[i,:] = node.coords
            i += 1
        
        return arr

    """
    Writes the discretization related sections into the stream variable dest

    Args:
        dest: stream variable (could for example be: with open('file.dat', 'w') as dest: ...)
    """
    def write(self, dest):

        self.compute_ids(zero_based=False)

        # write problem size
        num_ele = 0
        for elelist in self.elements.values():
            num_ele += len(elelist)
        
        write_title(dest, 'PROBLEM SIZE')
        write_option(dest, 'ELEMENTS', num_ele)
        write_option(dest, 'NODES', len(self.nodes))
        write_option(dest, 'DIM', 3)
        write_option(dest, 'MATERIALS', 9999) # Write dummy value

        # build design description
        topo_point = self.get_topology('dpoint')
        topo_line = self.get_topology('dline')
        topo_surf = self.get_topology('dsurf')
        topo_vol = self.get_topology('dvol')

        # write design description
        write_title(dest, 'DESIGN DESCRIPTION')
        write_option(dest, 'NDPOINT', len(topo_point))
        write_option(dest, 'NDLINE', len(topo_line))
        write_option(dest, 'NDSURF', len(topo_surf))
        write_option(dest, 'NDVOL', len(topo_vol))

        # write topology
        if len(topo_point) > 0:
            write_title(dest, 'DNODE-NODE TOPOLOGY')
            for topoid, nodelist in sorted(topo_point.items()):
                for nodeid in nodelist:
                    dest.write('NODE {0} DNODE {1}\n'.format(nodeid, topoid))

        if len(topo_line) > 0:
            write_title(dest, 'DLINE-NODE TOPOLOGY')
            for topoid, nodelist in sorted(topo_line.items()):
                for nodeid in nodelist:
                    dest.write('NODE {0} DLINE {1}\n'.format(nodeid, topoid))

        if len(topo_surf) > 0:
            write_title(dest, 'DSURF-NODE TOPOLOGY')
            for topoid, nodelist in sorted(topo_surf.items()):
                for nodeid in nodelist:
                    dest.write('NODE {0} DSURFACE {1}\n'.format(nodeid, topoid))

        if len(topo_vol) > 0:
            write_title(dest, 'DVOL-NODE TOPOLOGY')
            for topoid, nodelist in sorted(topo_vol.items()):
                for nodeid in nodelist:
                    dest.write('NODE {0} DVOLUME {1}\n'.format(nodeid, topoid))

        # write nodes
        write_title(dest, 'NODE COORDS')
        for node in self.nodes:
            node.write(dest)

        # write elements
        self.elements.write(dest)
        
        write_title(dest, 'END')

    """
    Returns the node topology of a specific type (dpoint, dline, dsurf, dvol).

    Args:
        topotype: Type of the topology (dpoint, dline, dsurf, dvol)
    
    Returns:
        Dictionary with nodeset as id and list of node ids as value
    """
    def get_topology(self, topotype: str):
        topo = {}
        for node in self.nodes:

            if node.id is None:
                raise RuntimeError('You have to compute ids before generating topology')

            for dp in getattr(node, topotype):
                if dp not in topo:
                    topo[dp] = []
                
                topo[dp].append(node.id)

        # check integrity
        if sorted(list(topo.keys())) != list(range(1, len(topo)+1)):
            raise RuntimeError('Topology contains empty nodesets!')

        return topo

    """
    Returns all nodes that belong to one of the dpoint nodesets defined in dnodes

    Args:
        dnodes: single integer or List of integer of nodeset ids
    
    Returns:
        List of nodes
    """
    def get_nodes_by_dnode(self, dnodes: List[int]):
        if not hasattr(dnodes, '__iter__'):
            dnodes = [dnodes]

        nodes: list = []

        for n in self.nodes:
            for dnode in dnodes:
                if dnode in n.dpoint:
                    nodes.append(n)
                    break

        return nodes
    
    """
    Returns all nodes that belong to one of the dline nodesets defined in dlines

    Args:
        dlines: single integer or List of integer of nodeset ids
    
    Returns:
        List of nodes
    """
    def get_nodes_by_dline(self, dlines: List[int]):
        if not hasattr(dlines, '__iter__'):
            dlines = [dlines]
        nodes: list = []

        for n in self.nodes:
            for dline in dlines:
                if dline in n.dline:
                    nodes.append(n)
                    break

        return nodes
    
    """
    Returns all nodes that belong to one of the dsurf nodesets defined in dsurfs

    Args:
        dsurfs: single integer or List of integer of nodeset ids
    
    Returns:
        List of nodes
    """
    def get_nodes_by_dsurf(self, dsurfs: List[int]):
        if not hasattr(dsurfs, '__iter__'):
            dsurfs = [dsurfs]
        nodes: list = []

        for n in self.nodes:
            for dsurf in dsurfs:
                if dsurf in n.dsurf:
                    nodes.append(n)
                    break

        return nodes

    """
    Returns all nodes that belong to one of the dvol nodesets defined in dvols

    Args:
        dvols: single integer or List of integer of nodeset ids
    
    Returns:
        List of nodes
    """
    def get_nodes_by_dvol(self, dvols: List[int]):
        if not hasattr(dvols, '__iter__'):
            dvols = [dvols]
        nodes: list = []

        for n in self.nodes:
            for dvol in dvols:
                if dvol in n.dvol:
                    nodes.append(n)
                    break

        return nodes

    """
    Static method that creates the discretizations file from the input lines of a .dat file

    Args:
        sections: Dictionary with header titles as keys and list of lines as value
    
    Retuns:
        Discretization object
    """
    @staticmethod
    def read(sections: Dict[str, List[str]], out: bool = False) -> 'Discretization':
        disc = Discretization()

        # read nodes
        for line in progress(sections['NODE COORDS'], out=out, label='Nodes'):
            if 'FNODE' in line:
                # this is a fiber node
                nodeid, _ = read_option_item(line, 'FNODE')
            else:
                nodeid, _ = read_option_item(line, 'NODE')
            

            if nodeid is None or nodeid == '':
                # this is not a node, probably a comment
                continue
            
            coords_str, _ = read_option_item(line, 'COORD', num=3)

            coords = np.array([float(i) for i in coords_str])

            node = Node(coords=coords)
            disc.nodes.append(node)

            # safety check for integrity of the dat file
            if int(nodeid) != len(disc.nodes):
                raise RuntimeError('Node ids in dat file have a gap at {0} != {1}!'.format(nodeid, len(disc.nodes)))
            
            # read fibers
            node.fibers = Fiber.parse_fibers(line)

        # read DPOINT topology
        if 'DNODE-NODE TOPOLOGY' in sections:
            for line in progress(sections['DNODE-NODE TOPOLOGY'], out=out, label='dnode topology'):
                nodeid_str, _ = read_option_item(line, 'NODE')
                
                if nodeid_str is None or nodeid_str == '':
                    # this is not a node, probably a comment
                    continue
                
                nodeid = int(nodeid_str)
                dpoint, _ = read_option_item(line, 'DNODE')

                if dpoint is None:
                    raise RuntimeError('Couldn\'t find DNODE option for node {0}'.format(nodeid))
                
                disc.nodes[nodeid-1].dpoint.append(int(dpoint))


        # read DLINE topology
        if 'DLINE-NODE TOPOLOGY' in sections:
            for line in progress(sections['DLINE-NODE TOPOLOGY'], out=out, label='dline topology'):
                nodeid_str, _ = read_option_item(line, 'NODE')
                
                if nodeid_str is None or nodeid_str == '':
                    # this is not a node, probably a comment
                    continue
                
                nodeid = int(nodeid_str)
                dline, _ = read_option_item(line, 'DLINE')

                if dline is None:
                    raise RuntimeError('Couldn\'t find DLINE option for node {0}'.format(nodeid))
                
                disc.nodes[nodeid-1].dline.append(int(dline))


        # read DSURF topology
        if 'DSURF-NODE TOPOLOGY' in sections:
            for line in progress(sections['DSURF-NODE TOPOLOGY'], out=out, label='dsurf topology'):
                nodeid_str, _ = read_option_item(line, 'NODE')
                
                if nodeid_str is None or nodeid_str == '':
                    # this is not a node, probably a comment
                    continue
                
                nodeid = int(nodeid_str)
                dsurf, _ = read_option_item(line, 'DSURFACE')

                if dsurf is None:
                    raise RuntimeError('Couldn\'t find DSURF option for node {0}'.format(nodeid))
                
                disc.nodes[nodeid-1].dsurf.append(int(dsurf))


        # read DVOL topology
        if 'DVOL-NODE TOPOLOGY' in sections:
            for line in progress(sections['DVOL-NODE TOPOLOGY'], out=out, label='dvol topology'):
                nodeid_str, _ = read_option_item(line, 'NODE')
                
                if nodeid_str is None or nodeid_str == '':
                    # this is not a node, probably a comment
                    continue
                
                nodeid = int(nodeid_str)
                dvol, _ = read_option_item(line, 'DVOLUME')

                if dvol is None:
                    raise RuntimeError('Couldn\'t find DVOL option for node {0}'.format(nodeid))
                
                disc.nodes[nodeid-1].dvol.append(int(dvol))

        # read elements
        disc.elements = ElementContainer.read_element_sections(sections, disc.nodes, out=out)

        return disc
    