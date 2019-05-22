import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, read_next_option
from collections import OrderedDict
import re


class Discretization:

    def __init__(self):
        self.nodes = []
        self.elements = {}
    
    def compute_ids(self):
        
        id: int = 1
        for node in self.nodes:
            node.id = id
            id += 1
        
        id: int = 1
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.id = id
                id += 1
    
    def reset(self):
        for node in self.nodes:
            node.reset()
        
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.reset()


    def write(self, dest):

        self.compute_ids()

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
            for topoid, nodelist in topo_point.items():
                for nodeid in nodelist:
                    dest.write('NODE {0} DNODE {1}\n'.format(nodeid, topoid))

        if len(topo_line) > 0:
            write_title(dest, 'DLINE-NODE TOPOLOGY')
            for topoid, nodelist in topo_line.items():
                for nodeid in nodelist:
                    dest.write('NODE {0} DLINE {1}\n'.format(nodeid, topoid))

        if len(topo_surf) > 0:
            write_title(dest, 'DSURF-NODE TOPOLOGY')
            for topoid, nodelist in topo_surf.items():
                for nodeid in nodelist:
                    dest.write('NODE {0} DSURFACE {1}\n'.format(nodeid, topoid))

        if len(topo_vol) > 0:
            write_title(dest, 'DVOL-NODE TOPOLOGY')
            for topoid, nodelist in topo_vol.items():
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

        if Element.FieldTypeALE in self.elements:
            write_title(dest, 'ALE ELEMENTS')
            for ele in self.elements[Element.FieldTypeALE]:
                ele.write(dest)

        if Element.FieldTypeFluid in self.elements:
            write_title(dest, 'FLUID ELEMENTS')
            for ele in self.elements[Element.FieldTypeFluid]:
                ele.write(dest)

        if Element.FieldTypeTransport in self.elements:
            write_title(dest, 'TRANSPORT ELEMENTS')
            for ele in self.elements[Element.FieldTypeTransport]:
                ele.write(dest)

        if Element.FieldTypeThermo in self.elements:
            write_title(dest, 'THERMO ELEMENTS')
            for ele in self.elements[Element.FieldTypeThermo]:
                ele.write(dest)

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
            
            if 'FIBER1' in line:
                node.fiber1 = np.array([float(i) for i in read_option_item(line, 'FIBER1', num=3)[0]])
            
            if 'FIBER2' in line:
                node.fiber2 = np.array([float(i) for i in read_option_item(line, 'FIBER2', num=3)[0]])
            
            if 'CIR' in line:
                node.fiber_cir = np.array([float(i) for i in read_option_item(line, 'CIR', num=3)[0]])
            
            if 'TAN' in line:
                node.fiber_tan = np.array([float(i) for i in read_option_item(line, 'TAN', num=3)[0]])
            
            if 'HELIX' in line:
                node.fiber_helix = np.array([float(i) for i in read_option_item(line, 'HELIX', num=3)[0]])
            
            if 'TRANS' in line:
                node.fiber_trans = np.array([float(i) for i in read_option_item(line, 'TRANS', num=3)[0]])


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
            
            # read remaining options
            # assume only one value per option, which must not be the case in general
            line = line[span[1]:]
            while True:
                line, key, value = read_next_option(line, num=1)

                if line is None:
                    break
                
                ele.options[key] = value
            
        
        return eles

class Node:

    def __init__(self, coords: np.array = np.zeros((3))):
        self.id = None
        self.coords: np.array = coords
        self.fiber1: np.array = None
        self.fiber2: np.array = None
        self.fiber_cir: np.array = None
        self.fiber_tan: np.array = None
        self.fiber_helix: np.array = None
        self.fiber_trans: np.array = None
        self.dpoint = []
        self.dline = []
        self.dsurf = []
        self.dvol = []
    
    def reset(self):
        self.id = None
    
    def write(self, dest):
        if self.fiber1 is not None or self.fiber2 is not None \
                or self.fiber_cir is not None or self.fiber_tan is not None \
                or self.fiber_helix is not None or self.fiber_trans is not None:
            dest.write('FNODE')
        else:
            dest.write('NODE')
        
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        dest.write(' {0} COORD {1}'.format(self.id, ' '.join([repr(i) for i in self.coords])))
    
        options: OrderedDict = OrderedDict()
        if self.fiber1 is not None:
            options['FIBER1'] = self.fiber1
        if self.fiber2 is not None:
            options['FIBER2'] = self.fiber2
        if self.fiber_cir is not None:
            options['CIR'] = self.fiber_cir
        if self.fiber_tan is not None:
            options['TAN'] = self.fiber_tan
        if self.fiber_helix is not None:
            options['HELIX'] = self.fiber_helix
        if self.fiber_trans is not None:
            options['TRANS'] = self.fiber_trans
        
        if len(options) > 0:
            dest.write(' ')
            write_option_list(dest, options, newline=False)
        dest.write('\n')


class Element:
    FieldTypeStructure: str = 'structure'
    FieldTypeFluid: str = 'fluid'
    FieldTypeALE: str = 'ale'
    FieldTypeTransport: str = 'transport'
    FieldTypeThermo: str = 'thermo'

    def __init__(self, el_type: str, shape: str, nodes: List[Node],
            options: OrderedDict = OrderedDict()):
        self.id = None
        self.type = el_type
        self.shape = shape
        self.nodes = nodes
        self.options = options
    
    def reset(self):
        self.id = None
    
    def write(self, dest):
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        dest.write('{0} {1} '.format(self.id, self.type))

        options: OrderedDict = OrderedDict()
        options[self.shape] = [i.id for i in self.nodes]
        options.update(self.options)

        write_option_list(dest, options)


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