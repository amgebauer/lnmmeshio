from .ioutils import read_option_item, write_title
from .progress import progress


class Nodeset:
    def __init__(self, id, name=None):
        self.id = id
        self.nodes = set()
        self.name = name

    @staticmethod
    def get_typename_long():
        raise NotImplementedError("Need to implement get_typename_long()")

    @staticmethod
    def get_typename_short():
        raise NotImplementedError("Need to implement get_typename_short()")

    def reset(self):
        self.id = None

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.add(node)

    def add_nodes(self, nodes):
        for n in nodes:
            self.nodes.add(n)

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __getitem__(self, x):
        return list(self.nodes)[x]

    def get_lines(self):
        lines = []
        for n in self:
            lines.append(
                "NODE {0} D{1} {2}".format(
                    n.id, self.get_typename_long().upper(), self.id
                )
            )

        return lines

    def write(self, dest):
        for l in self.get_lines():
            dest.write("{0}\n".format(l))

    @staticmethod
    def base_read(lines, nodes, nodeset_cls, out=False):
        id2pos = {}
        nodesets = []

        next_number = 0
        for line in progress(lines, out=out, label="dnode topology"):

            nodeid_str, _ = read_option_item(line, "NODE")
            if nodeid_str is None or nodeid_str == "":
                # this is not a node, probably a comment
                continue

            try:
                nodeid = int(nodeid_str)
            except ValueError:
                print("Could not read {0} as int".format(nodeid_str))
                continue
            dpoint, _ = read_option_item(
                line, "D{0}".format(nodeset_cls.get_typename_long())
            )
            if dpoint is None:
                raise RuntimeError(
                    "Couldn't find D{0} option for {0} {1}. Line is \n\n{2}".format(
                        nodeset_cls.get_typename_long(), nodeid, line
                    )
                )

            if dpoint not in id2pos:
                id2pos[dpoint] = next_number
                next_number += 1
                if int(dpoint) != next_number:
                    raise RuntimeError(
                        "The nodeset numbering will not be preserved during read! Expecting {0}, got {1}".format(
                            next_number, dpoint
                        )
                    )
                nodesets.append(nodeset_cls(dpoint))

            nodesets[id2pos[dpoint]].add_node(nodes[nodeid - 1])

        return nodesets


class PointNodeset(Nodeset):
    def __init__(self, id, name=None):
        super(PointNodeset, self).__init__(id, name=name)

    @staticmethod
    def get_typename_long():
        return "NODE"

    @staticmethod
    def get_typename_short():
        return "NODE"

    @staticmethod
    def get_section():
        return "DNODE-NODE TOPOLOGY"

    @staticmethod
    def write_header(dest):
        write_title(dest, PointNodeset.get_section())

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, PointNodeset, out=out)


class LineNodeset(Nodeset):
    def __init__(self, id, name=None):
        super(LineNodeset, self).__init__(id, name=name)

    @staticmethod
    def get_typename_long():
        return "LINE"

    @staticmethod
    def get_typename_short():
        return "LINE"

    @staticmethod
    def get_section():
        return "DLINE-NODE TOPOLOGY"

    @staticmethod
    def write_header(dest):
        write_title(dest, LineNodeset.get_section())

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, LineNodeset, out=out)


class SurfaceNodeset(Nodeset):
    def __init__(self, id, name=None):
        super(SurfaceNodeset, self).__init__(id, name=name)

    @staticmethod
    def get_typename_long():
        return "SURFACE"

    @staticmethod
    def get_typename_short():
        return "SURF"

    @staticmethod
    def get_section():
        return "DSURF-NODE TOPOLOGY"

    @staticmethod
    def write_header(dest):
        write_title(dest, SurfaceNodeset.get_section())

    @staticmethod
    def read(lines, nodes, out=False):
        return Nodeset.base_read(lines, nodes, SurfaceNodeset, out=out)


class VolumeNodeset(Nodeset):
    def __init__(self, id, name=None):
        super(VolumeNodeset, self).__init__(id, name=name)

    @staticmethod
    def get_typename_long():
        return "VOLUME"

    @staticmethod
    def get_typename_short():
        return "VOL"

    @staticmethod
    def get_section():
        return "DVOL-NODE TOPOLOGY"

    @staticmethod
    def write_header(dest):
        write_title(dest, VolumeNodeset.get_section())

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

    def get_unused_id(self):

        nsid = 1
        while nsid in self.id2pos.keys():
            nsid += 1

        return nsid

    def finalize(self):
        # return nodeset sorted by its id to preserve the id
        return [self.nodesets[self.id2pos[i]] for i in sorted(list(self.id2pos))]


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
