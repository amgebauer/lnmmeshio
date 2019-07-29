from .ioutils import write_title, read_option_item
from .progress import progress

class Nodeset:
    def __init__(self, id):
        self.id = id
        self.nodes = []
    
    @staticmethod
    def get_typename_long():
        raise NotImplementedError("Need to implement get_typename_long()")
    
    @staticmethod
    def get_typename_short():
        raise NotImplementedError("Need to implement get_typename_short()")

    def reset(self):
        self.id = None
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def add_nodes(self, nodes):
        self.nodes.extend(nodes)
    
    def __getitem__(self, key):
        return self.nodes[key]

    def __len__(self):
        return len(self.nodes)
    
    def __iter__(self):
        self.i = 0
        return self
    
    def __next__(self):
        self.i += 1
        if self.i > len(self):
            raise StopIteration()
        return self.nodes[self.i-1]
    
    def write(self, dest):
        for n in self:
            dest.write('NODE {0} D{1} {2}\n'.format(n.id, self.get_typename_long().upper(), self.id))

    @staticmethod
    def base_read(lines, nodes, nodeset_cls, out=False):
        id2pos = {}
        nodesets = []

        next_number = 0
        for line in progress(lines, out=out, label='dnode topology'):

            nodeid_str, _ = read_option_item(line, 'NODE')
            if nodeid_str is None or nodeid_str == '':
                # this is not a node, probably a comment
                continue
            
            try:
                nodeid = int(nodeid_str)
            except ValueError:
                print('Could not read {0} as int'.format(nodeid_str))
                continue
            dpoint, _ = read_option_item(line, 'D{0}'.format(nodeset_cls.get_typename_long()))
            if dpoint is None:
                raise RuntimeError('Couldn\'t find D{0} option for {0} {1}. Line is \n\n{2}'.format(nodeset_cls.get_typename_long(), nodeid, line))
            
            if dpoint not in id2pos:
                id2pos[dpoint] = next_number
                next_number += 1
                if int(dpoint) != next_number:
                    raise RuntimeError("The nodeset numbering will not be preserved during read! Expecting {0}, got {1}".format(next_number, dpoint))
                nodesets.append(nodeset_cls(dpoint))
            
            nodesets[id2pos[dpoint]].add_node(nodes[nodeid-1])
        
        return nodesets
                
class PointNodeset(Nodeset):

    def __init__(self, id):
        super(PointNodeset, self).__init__(id)

    @staticmethod
    def get_typename_long():
        return "NODE"
    
    @staticmethod
    def get_typename_short():
        return "NODE"
    
    @staticmethod
    def write_header(dest):
        write_title(dest, 'DNODE-NODE TOPOLOGY')

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, PointNodeset, out=out)

class LineNodeset(Nodeset):

    def __init__(self, id):
        super(LineNodeset, self).__init__(id)

    @staticmethod
    def get_typename_long():
        return "LINE"
    
    @staticmethod
    def get_typename_short():
        return "LINE"
    
    @staticmethod
    def write_header(dest):
        write_title(dest, 'DLINE-NODE TOPOLOGY')

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, LineNodeset, out=out)

class SurfaceNodeset(Nodeset):

    def __init__(self, id):
        super(SurfaceNodeset, self).__init__(id)

    @staticmethod
    def get_typename_long():
        return "SURFACE"
    
    @staticmethod
    def get_typename_short():
        return "SURF"
    
    @staticmethod
    def write_header(dest):
        write_title(dest, 'DSURF-NODE TOPOLOGY')

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, SurfaceNodeset, out=out)

class VolumeNodeset(Nodeset):

    def __init__(self, id):
        super(VolumeNodeset, self).__init__(id)

    @staticmethod
    def get_typename_long():
        return "VOLUME"
    
    @staticmethod
    def get_typename_short():
        return "VOL"
    
    @staticmethod
    def write_header(dest):
        write_title(dest, 'DVOL-NODE TOPOLOGY')

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, VolumeNodeset, out=out)

class NodesetBuilder:

    def __init__(self, nstype):
        self.nstype = nstype
        self.nodesets = []
        self.id2pos = {}

    def add(self, node, id):
        if id not in self.id2pos:
            self.id2pos[id] = len(self.nodesets)
            self.nodesets.append(self.nstype(id))
        
        self.nodesets[self.id2pos[id]].add_node(node)
    
    def finalize(self):
        return self.nodesets

class PointNodesetBuilder(NodesetBuilder):
    def __init__(self):
        super(PointNodesetBuilder, self).__init__(PointNodeset)

class LineNodesetBuilder(NodesetBuilder):
    def __init__(self):
        super(LineNodesetBuilder, self).__init__(LineNodeset)

class SurfaceNodesetBuilder(NodesetBuilder):
    def __init__(self):
        super(SurfaceNodesetBuilder, self).__init__(SurfaceNodeset)

class VolumeNodesetBuilder(NodesetBuilder):
    def __init__(self):
        super(VolumeNodesetBuilder, self).__init__(VolumeNodeset)