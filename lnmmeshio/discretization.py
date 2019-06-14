import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from collections import OrderedDict
import re

"""
This class holds the discretization, consisting out of nodes and elements. The nodes and
elements itself hold their data (coords, element type, ...)
"""
class Discretization:

    """
    Initialize Discretization class with empty nodes and zero elements
    """
    def __init__(self):
        self.nodes = []
        self.elements = {}
    
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
        if Element.FieldTypeStructure in self.elements:
            write_title(dest, 'STRUCTURE ELEMENTS')
            for ele in self.elements[Element.FieldTypeStructure]:
                ele.write(dest)

        if Element.FieldTypeFluid in self.elements:
            write_title(dest, 'FLUID ELEMENTS')
            for ele in self.elements[Element.FieldTypeFluid]:
                ele.write(dest)

        if Element.FieldTypeALE in self.elements:
            write_title(dest, 'ALE ELEMENTS')
            for ele in self.elements[Element.FieldTypeALE]:
                ele.write(dest)

        if Element.FieldTypeTransport in self.elements:
            write_title(dest, 'TRANSPORT ELEMENTS')
            for ele in self.elements[Element.FieldTypeTransport]:
                ele.write(dest)

        if Element.FieldTypeThermo in self.elements:
            write_title(dest, 'THERMO ELEMENTS')
            for ele in self.elements[Element.FieldTypeThermo]:
                ele.write(dest)
        
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
    def read(sections: Dict[str, List[str]]) -> 'Discretization':
        disc = Discretization()

        # read nodes
        for line in sections['NODE COORDS']:
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
            for line in sections['DNODE-NODE TOPOLOGY']:
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
            for line in sections['DLINE-NODE TOPOLOGY']:
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
            for line in sections['DSURF-NODE TOPOLOGY']:
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
            for line in sections['DVOL-NODE TOPOLOGY']:
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
        if 'STRUCTURE ELEMENTS' in sections:
            disc.elements[Element.FieldTypeStructure] = Discretization.read_elements(disc.nodes, sections['STRUCTURE ELEMENTS'])
        
        if 'FLUID ELEMENTS' in sections:
            disc.elements[Element.FieldTypeFluid] = Discretization.read_elements(disc.nodes, sections['FLUID ELEMENTS'])
        
        if 'ALE ELEMENTS' in sections:
            disc.elements[Element.FieldTypeALE] = Discretization.read_elements(disc.nodes, sections['ALE ELEMENTS'])
        
        if 'TRANSPORT ELEMENTS' in sections:
            disc.elements[Element.FieldTypeTransport] = Discretization.read_elements(disc.nodes, sections['TRANSPORT ELEMENTS'])
        
        if 'THERMO ELEMENTS' in sections:
            disc.elements[Element.FieldTypeThermo] = Discretization.read_elements(disc.nodes, sections['THERMO ELEMENTS'])


        return disc
    
    """
    Static method that reads the list of elements

    Args:
        nodes: List of nodes (order is important: first node in list must be the one with id 1)
        lines: List of string that represent the lines of the corresponding element section
    
    Returns:
        List of elements
    """
    @staticmethod
    def read_elements(nodes: List['Node'], lines: List[str]):
        eles = []

        re_ele = re.compile(r'^[ ]*([0-9]+)[ ]+(\S+)[ ]+(\S+)[ ]+')
        for line in lines:
            line = line.split('//', 1)[0]
            # parse ele id, type and shape
            ele_match = re_ele.search(line)
            if not ele_match:
                continue

            ele_id = int(ele_match.group(1))
            ele_type = ele_match.group(2)
            ele_shape = ele_match.group(3)
            
            node_ids_str, span = read_option_item(line, ele_shape, Element.get_num_nodes(ele_shape))
            node_ids = [int(i) for i in node_ids_str]

            ele = Element(ele_type, ele_shape,
                [ nodes[i-1] for i in node_ids]
            )
            eles.append(ele)

            # safety check for integrity of the dat file
            if int(ele_id) != len(eles):
                raise RuntimeError('Element ids in dat file have a gap at {0}!={1}!'.format(ele_id, len(eles)))
            
            # read fibers
            ele.fibers = Fiber.parse_fibers(line)

            # read remaining options
            # assume only one value per option, which must not be the case in general
            line = line[span[1]:]
            while True:
                line, key = read_next_key(line)
                if line is None:
                    break

                num = 1
                if Fiber.get_fiber_type(key) is not None:
                    num = 3

                line, value = read_next_value(line, num=num)

                if line is None:
                    break
                
                ele.options[key] = value
            
        
        return eles

"""
Class that holds all information of nodes like coords, fibers, nodesets (and additional data)
"""
class Node:

    """
    Initialize node at the coordinades coords

    Args:
        coords: np.array((3)) Coordinates of the node
    """
    def __init__(self, coords: np.array = np.zeros((3))):
        self.id = None
        self.coords: np.array = coords
        self.fibers: Dict[str, Fiber] = {}
        self.dpoint = []
        self.dline = []
        self.dsurf = []
        self.dvol = []
        self.data = {}
    
    """
    Sets the id to None
    """
    def reset(self):
        self.id = None
    
    """
    Writes the corresponding line in to the stream variable

    Args:
        dest: stream variable where to write the line
    """
    def write(self, dest):
        if len(self.fibers) > 0:
            dest.write('FNODE')
        else:
            dest.write('NODE')
        
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        dest.write(' {0} COORD {1}'.format(self.id, ' '.join([repr(i) for i in self.coords])))
        
        for k, f in self.fibers.items():
            dest.write(' ')
            f.write(dest, k)

        dest.write('\n')


"""
Class that holds all information of fibers
"""
class Fiber:
    # defintion of different fibers (add if more are necessary)
    TypeFiber1: str = 'fiber1'
    TypeFiber2: str = 'fiber2'
    TypeCir: str = 'cir'
    TypeTan: str = 'tan'


    """
    Initialize fiber vector in direction of fib

    Args:
        fib: Unit vector pointing in fiber direction np.array((3))
    """
    def __init__(self, fib: np.array):
        self.fiber = fib

    """
    Writes the corresponding section in the dat file into the stream type variable dest

    Args:
        dest: stream variable where to write the fiber
        inp_type: type of fiber (defined as static variable)
    """
    def write(self, dest, inp_type):
        ftype = None

        if inp_type == Fiber.TypeFiber1:
            ftype = "FIBER1"
        elif inp_type == Fiber.TypeFiber2:
            ftype = "FIBER2"
        elif inp_type == Fiber.TypeCir:
            ftype = "CIR"
        elif inp_type == Fiber.TypeTan:
            ftype = "TAN"
        else:
            raise ValueError('Unknown fiber type {0}'.format(inp_type))

        write_option_list(dest, {
            ftype: self.fiber
        }, newline=False)
    
    """
    Returns the corresponding fiber type enum from the definition in the dat file

    Args:
        fstr: Fiber name as defined in the dat file
    
    Returns:
        Fiber enum as defined on top of the class
    """
    @staticmethod
    def get_fiber_type(fstr: str):
        if fstr == 'FIBER1':
            return Fiber.TypeFiber1
        elif fstr == 'FIBER2':
            return Fiber.TypeFiber2
        elif fstr == 'CIR':
            return Fiber.TypeCir
        elif fstr == 'TAN':
            return Fiber.TypeTan
        else:
            return None

    """
    Parses the fibers from the line and returns a dict of fiber objects

    Args:
        line: String of the line
    
    Returns:
        dict with fiber type as key and fiber object as value
    """
    @staticmethod
    def parse_fibers(line: str) -> dict:
        fibs: dict = {}
        if 'FIBER1' in line:
            fibs[Fiber.TypeFiber1] = Fiber(np.array([float(i) for i in read_option_item(line, 'FIBER1', num=3)[0]]))

        if 'FIBER2' in line:
            fibs[Fiber.TypeFiber2] = Fiber(np.array([float(i) for i in read_option_item(line, 'FIBER2', num=3)[0]]))

        if 'CIR' in line:
            fibs[Fiber.TypeCir] = Fiber(np.array([float(i) for i in read_option_item(line, 'CIR', num=3)[0]]))

        if 'TAN' in line:
            fibs[Fiber.TypeTan] = Fiber(np.array([float(i) for i in read_option_item(line, 'TAN', num=3)[0]]))

        return fibs

"""
Class holding the data of one element
"""
class Element:
    FieldTypeStructure: str = 'structure'
    FieldTypeFluid: str = 'fluid'
    FieldTypeALE: str = 'ale'
    FieldTypeTransport: str = 'transport'
    FieldTypeThermo: str = 'thermo'

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