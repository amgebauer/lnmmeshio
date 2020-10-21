#
# Maintainer: Amadeus Gebauer
#
# This is the interface between the meshio package and our Discretization description
# May not work perfectly
#
import numpy as np

import meshio

from .discretization import Discretization, Node
from .element.line2 import Line2
from .element.line3 import Line3
from .element.parse_element import create_element
from .element.quad4 import Quad4
from .element.tri3 import Tri3
from .element.tri6 import Tri6
from .nodeset import (
    LineNodeset,
    LineNodesetBuilder,
    PointNodeset,
    PointNodesetBuilder,
    SurfaceNodeset,
    SurfaceNodesetBuilder,
    VolumeNodeset,
    VolumeNodesetBuilder,
)
from .progress import progress

cell_nodes = {
    "line": 2,
    "triangle": 3,
    "tetra": 4,
    "tetra10": 10,
    "pyramid": 5,
    "hexahedron": 8,
    "hexahedron20": 20,
    "hexahedron27": 27,
    "wedge": 6,
    "quad": 4,
    "quad9": 9,
    "vertex": 1,
}

cell_disc_eles = {
    "line": "UNKNOWN",
    "triangle": "UNKNOWN",
    "tetra": "SOLIDT4",
    "tetra10": "PYRAMID5",
    "pyramid": "UNKNOWN",
    "hexahedron": "SOLIDH8",
    "hexahedron20": "SOLIDH20",
    "hexahedron27": "SOLIDH27",
    "wedge": "UNKNOWN",
    "quad": "UNKNOWN",
    "quad9": "UNKNOWN",
}

cell_disc_shape = {
    "line": "LINE2",
    "triangle": "TRI3",
    "tetra": "TET4",
    "tetra10": "TET10",
    "pyramid": "PYRAMID5",
    "hexahedron": "HEX8",
    "hexahedron20": "HEX20",
    "hexahedron27": "HEX27",
    "wedge": "WEDGE6",
    "quad": "QUAD4",
    "quad9": "QUAD9",
}

_cell_data_id_names = ["medit:ref", "gmsh:geometrical"]

# invert cell_disc_shape
disc_shape_cell = {v: k for k, v in cell_disc_shape.items()}

cell_to_dim = {
    "vertex": 0,
    "line": 1,
    "line3": 1,
    "triangle": 2,
    "triangle6": 2,
    "tetra": 3,
    "tetra10": 3,
    "pyramid": 3,
    "hexahedron": 3,
    "hexahedron20": 3,
    "hexahedron27": 3,
    "wedge": 3,
    "quad": 2,
    "quad9": 2,
}

# meshio used vtk node ordering
# with this array, we reorder the nodes
ele_node_order_vtk2baci = {
    "LINE2": list(range(0, 2)),
    "TRI3": list(range(0, 3)),
    "TET4": list(range(0, 4)),
    "TET10": list(range(0, 10)),
    "PYRAMID5": list(range(0, 5)),
    "HEX8": list(range(0, 8)),
    "HEX20": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        16,
        17,
        18,
        19,
        12,
        13,
        14,
        15,
    ],  # verify ?
    "HEX27": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        16,
        17,
        18,
        19,
        12,
        13,
        14,
        15,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
    ],  # verify ?
    "WEDGE6": list(range(0, 6)),
    "QUAD4": list(range(0, 4)),
    "QUAD9": list(range(0, 9)),
}


def mesh2Discretization(mesh: meshio.Mesh) -> Discretization:

    # create empty discretization
    disc = Discretization()

    # mesh.points -> disc.nodes
    # mesh.cells -> disc.elements[Element.FieldTypeStructure]
    # node_sets -> are stored in disc.nodes

    # create Nodes from points
    for i, coord in progress(enumerate(mesh.points), label="Create nodes"):
        n = Node(coord)

        for key, v in mesh.point_data.items():
            n.data[key] = v[i]

        disc.nodes.append(n)

    # get the maximum element dimension, which is the dimension of the mesh
    maxdim = max([cell_to_dim[cells[0]] for cells in mesh.cells])

    # create Elements from cells
    disc.elements.structure = []
    pointnsbuilder = PointNodesetBuilder()
    linensbuilder = LineNodesetBuilder()
    surfnsbuilder = SurfaceNodesetBuilder()
    volumensbuilder = VolumeNodesetBuilder()

    for cellgroupid, (celltype, cells) in enumerate(mesh.cells):
        if celltype not in cell_nodes:
            raise Exception(
                "The cell type {0} is currently not implemented".format(celltype)
            )

        for cellid, cell in enumerate(
            progress(cells, label="Create {0} elements".format(celltype))
        ):
            # read nodes that belong to the cells
            nodes = []

            # in case of a vertex, cell is just an integer
            cell = np.array(cell).reshape((-1))

            for nodeids in cell:
                nodes.append(disc.nodes[nodeids])

            # cells with the same dimension as the mesh dimensions are normal cells
            # cells with a lower dimension are treated as surface, line or node
            # definitions
            eledim = cell_to_dim[celltype]
            if maxdim == eledim:
                # this is a normal element
                ele = create_element(
                    cell_disc_eles[celltype],
                    cell_disc_shape[celltype],
                    # also need to reorder nodes in a few element types
                    [
                        nodes[i]
                        for i in ele_node_order_vtk2baci[cell_disc_shape[celltype]]
                    ],
                )
                disc.elements.structure.append(ele)

                # extract material info from cell data
                matid: int = _get_material_from_cell_data(
                    mesh.cell_data, cellgroupid, cellid
                )
                if matid == None:
                    matid = 1
                ele.options["MAT"] = matid

                # extract cell data
                for key, data in mesh.cell_data.items():
                    ele.data[key] = data[cellgroupid][cellid]

            else:
                # this is a lower-dimensional element
                # treat as surface-, line- or point-nodeset definition

                # extract nodeset info from cell data
                nsid: int = int(
                    _get_nodesetid_from_cell_data(mesh.cell_data, cellgroupid, cellid)
                )

                for node in nodes:
                    if eledim == 0:
                        pointnsbuilder.add(node, nsid)
                    elif eledim == 1:
                        linensbuilder.add(node, nsid)
                    elif eledim == 2:
                        surfnsbuilder.add(node, nsid)

    # go through nodesets
    for name, nodes in mesh.point_sets.items():
        if "volume" in name:
            nsid = volumensbuilder.get_unused_id()
            for n in nodes:
                volumensbuilder.add(disc.nodes[n], nsid)
        if "surface" in name:
            nsid = surfnsbuilder.get_unused_id()
            for n in nodes:
                surfnsbuilder.add(disc.nodes[n], nsid)
        elif "line" in name:
            nsid = linensbuilder.get_unused_id()
            for n in nodes:
                linensbuilder.add(disc.nodes[n], nsid)
        elif "point" in name:
            nsid = pointnsbuilder.get_unused_id()
            for n in nodes:
                pointnsbuilder.add(disc.nodes[n], nsid)

    disc.volumenodesets = volumensbuilder.finalize()
    disc.pointnodesets = pointnsbuilder.finalize()
    disc.linenodesets = linensbuilder.finalize()
    disc.surfacenodesets = surfnsbuilder.finalize()

    disc.finalize()
    return disc


def discretization2mesh(dis: Discretization) -> meshio.Mesh:
    dis.compute_ids(zero_based=True)

    points = dis.get_node_coords()

    point_data = {}

    for i, n in enumerate(dis.nodes):

        for k, v in n.data.items():
            if k not in point_data:
                point_data[k] = np.zeros(tuple([len(dis.nodes)] + list(v.shape)))

            point_data[k][i] = v

    cells = []
    cell_data = {}

    # store elements
    for eletype in dis.elements.values():
        for ele in eletype:
            celltype = disc_shape_cell[ele.shape]

            newgroup = False

            if len(cells) == 0 or cells[-1]["type"] != celltype:
                cells.append(
                    {"type": celltype, "arr": np.zeros((0, len(ele.nodes)), dtype=int),}
                )
                newgroup = True

            cells[-1]["arr"] = np.append(
                cells[-1]["arr"],
                np.array([n.id for n in ele.nodes]).reshape((1, -1)),
                axis=0,
            )
            # store material id
            for variable_name in _cell_data_id_names:
                if variable_name not in cell_data:
                    cell_data[variable_name] = []

                if newgroup:
                    cell_data[variable_name].append(np.array([], dtype=int))

                cell_data[variable_name][-1] = np.append(
                    cell_data[variable_name][-1], int(ele.options["MAT"][0])
                )

    # store nodesets
    print("Exporting of nodesets from dat to other file formats does not work")

    cells_new = [(cell["type"], cell["arr"]) for cell in cells]

    mesh: meshio.Mesh = meshio.Mesh(
        points, cells_new, cell_data=cell_data, point_data=point_data
    )

    dis.reset()

    return mesh


def _get_material_from_cell_data(celldata, cellgroupid, cellid):
    for name in _cell_data_id_names:
        if name in celldata:
            return int(celldata[name][cellgroupid][cellid])

    return None


def _get_nodesetid_from_cell_data(celldata, cellgroupid, cellid):
    for name in _cell_data_id_names:
        if name in celldata:
            return int(celldata[name][cellgroupid][cellid])

    return None
