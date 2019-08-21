# 
# Maintainer: Amadeus Gebauer
# 
# This is the interface between the meshio package and our Discretization description
# May not work perfectly
# 
import numpy as np
import meshio
from .discretization import Element, Discretization, Node
from .element.parse_element import create_element
from .progress import progress
from .element.line2 import Line2
from .element.line3 import Line3
from .element.tri3 import Tri3
from .element.tri6 import Tri6
from .element.quad4 import Quad4
from .nodeset import PointNodeset, PointNodesetBuilder, LineNodeset, LineNodesetBuilder, SurfaceNodeset, SurfaceNodesetBuilder, VolumeNodeset, VolumeNodesetBuilder

cell_nodes = {
    'line': 2,
    'triangle': 3,
    'tetra': 4,
    'tetra10': 10,
    'pyramid': 5,
    'hexahedron': 8,
    'hexahedron20': 20,
    'hexahedron27': 27,
    'wedge': 6,
    'quad': 4,
    'quad9': 9,
    'vertex': 1
}

cell_disc_eles = {
    'line': 'UNKNOWN',
    'triangle': 'UNKNOWN',
    'tetra': 'SOLIDT4SCATRA',
    'tetra10': 'PYRAMID5',
    'pyramid': 'UNKNOWN',
    'hexahedron': 'SOLIDH8SCATRA',
    'hexahedron20': 'UNKNOWN',
    'hexahedron27': 'SOLIDH27SCATRA',
    'wedge': 'UNKNOWN',
    'quad': 'UNKNOWN',
    'quad9': 'UNKNOWN'
}

cell_disc_shape = {
    'line': 'LINE2',
    'triangle': 'TRI3',
    'tetra': 'TET4',
    'tetra10': 'TET10',
    'pyramid': 'PYRAMID5',
    'hexahedron': 'HEX8',
    'hexahedron20': 'HEX20',
    'hexahedron27': 'HEX27',
    'wedge': 'WEDGE6',
    'quad': 'QUAD4',
    'quad9': 'QUAD9'
}

_cell_data_id_names = ['medit:ref', 'gmsh:geometrical']

# invert cell_disc_shape
disc_shape_cell = {v: k for k, v in cell_disc_shape.items()}

cell_to_dim = {
    'vertex': 0,
    'line': 1,
    'line3': 1,
    'triangle': 2,
    'triangle6': 2,
    'tetra': 3,
    'tetra10': 3,
    'pyramid': 3,
    'hexahedron': 3,
    'hexahedron20': 3,
    'hexahedron27': 3,
    'wedge': 3,
    'quad': 2,
    'quad9': 2
}

# meshio used vtk node ordering
# with this array, we reorder the nodes
ele_node_order_vtk2baci = {
    'LINE2': list(range(0,2)),
    'TRI3': list(range(0,3)),
    'TET4': list(range(0,4)),
    'TET10': list(range(0,10)),
    'PYRAMID5': list(range(0,5)),
    'HEX8': list(range(0,8)),
    'HEX20': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 12, 13, 14, 15], # verify ?
    'HEX27': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19, 12, 13, 14, 15, 20, 21, 22, 23, 24, 25, 26], # verify ?
    'WEDGE6': list(range(0,6)),
    'QUAD4': list(range(0,4)),
    'QUAD9': list(range(0,9))
}

def mesh2Discretization(mesh: meshio.Mesh) -> Discretization:

    # create empty discretization
    disc = Discretization()

    # mesh.points -> disc.nodes
    # mesh.cells -> disc.elements[Element.FieldTypeStructure]
    # node_sets -> are stored in disc.nodes

    # create Nodes from points
    for i, coord in progress(enumerate(mesh.points), label='Create nodes'):
        n = Node(coord)

        for key, v in mesh.point_data.items():
            n.data[key] = v[i]

        disc.nodes.append(
            n
        )

    # get the maximum element dimension, which is the dimension of the mesh
    maxdim = max([cell_to_dim[celltype] for celltype in mesh.cells.keys()])
    
    # create Elements from cells
    disc.elements.structure = []
    pointnsbuilder = PointNodesetBuilder()
    linensbuilder = LineNodesetBuilder()
    surfnsbuilder = SurfaceNodesetBuilder()
    for celltype, cells in mesh.cells.items():

        if celltype not in cell_nodes:
            raise Exception('The cell type {0} is currently not implemented'.format(celltype))
        
        cellindex: int = 0
        for cell in progress(cells, label='Create {0} elements'.format(celltype)):
            # read nodes that belong to the cells
            nodes = []

            # in case of a vertex, cell is just an integer
            cell = np.array(cell).reshape((-1))

            for nodeids in cell:
                nodes.append(disc.nodes[nodeids])

            # cells with the same dimension as the mesh dimensions are normal cells
            # cells with a lower dimension are treated as surface, line or node definitions
            eledim = cell_to_dim[celltype]
            if maxdim == eledim:
                # this is a normal element
                ele = create_element(
                    cell_disc_eles[celltype],
                    cell_disc_shape[celltype],
                    # also need to reorder nodes in a few element types
                    [nodes[i] for i in ele_node_order_vtk2baci[cell_disc_shape[celltype]]]
                )
                disc.elements.structure.append(ele)

                # extract material info from cell data
                matid: int = _get_id_from_cell_data(mesh.cell_data[celltype])[cellindex]
                ele.options['MAT'] = matid

                # extract cell data
                for key, value in mesh.cell_data[celltype].items():
                    ele.data[key] = value[cellindex]


            else:
                # this is a lower-dimensional element
                # treat as surface-, line- or point-nodeset definition
                
                # extract nodeset info from cell data
                nsid: int = int(_get_id_from_cell_data(mesh.cell_data[celltype])[cellindex])

                for node in nodes:
                    if eledim == 0:
                        pointnsbuilder.add(node, nsid)
                    elif eledim == 1:
                        linensbuilder.add(node, nsid)
                    elif eledim == 2:
                        surfnsbuilder.add(node, nsid)
            
            cellindex += 1

    disc.pointnodesets = pointnsbuilder.finalize()
    disc.linenodesets = linensbuilder.finalize()
    disc.surfacenodesets = surfnsbuilder.finalize()

    # copy element data
    for celltype, cells in mesh.cells.items():
        pass
    
    disc.finalize()
    return disc

def discretization2mesh(dis: Discretization) -> meshio.Mesh:
    dis.compute_ids(zero_based=True)

    points = dis.get_node_coords()

    point_data = {}

    for i, n in enumerate(dis.nodes):

        for k, v in n.data.items():
            if k not in point_data:
                point_data[k] = np.zeros(tuple([len(dis.nodes)]+list(v.shape)))
            
            point_data[k][i] = v

    cells = {}
    cell_data = {}

    for eletype in dis.elements.values():
        for ele in eletype:
            celltype = disc_shape_cell[ele.shape]

            if celltype not in cells:
                cells[celltype] = np.zeros((0, cell_nodes[celltype]), dtype=int)
                cell_data[celltype] = {
                    name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                }
            cells[celltype] = np.append(cells[celltype], ele.get_node_ids().reshape((1,-1)), axis=0)

            for key, value in ele.data.items():
                if key not in cell_data[celltype]:
                    cell_data[celltype][key] = value.reshape(tuple([1]+list(value.shape)))
                else:
                    cell_data[celltype][key] = np.append(cell_data[celltype][key], value.reshape(tuple([1]+list(value.shape))), axis=0)

            # store material id
            if 'MAT' in ele.options:
                for name in _cell_data_id_names:
                    matid = ele.options['MAT']
                    if isinstance(matid, list):
                        matid = matid[0]
                    cell_data[celltype][name] = np.append(cell_data[celltype][name], int(matid))
            
            # go over element faces
            for face in ele.get_faces():
                # check, whether all nodes of this face belong to a same dsurf
                union_set = face.get_dsurfs()

                # create line cells with id dlineid
                if face.shape == Tri3.ShapeName:
                    facetype = 'triangle'
                elif face.shape == Tri6.ShapeName:
                    facetype = 'triangle6'
                elif face.shape == Quad4.ShapeName:
                    facetype = 'quad'
                else:
                    facetype = None
                
                # unimplemented face type -> throw error
                if facetype is None:
                    raise RuntimeError('This kind of face is not implemented yet! Face of {0} with {1} nodes (type {2})'.format(ele.shape, face.get_num_nodes(), face.shape))

                for dsurfid in union_set:
                    # create surface cells with id dsurfid

                    # check, whether there is already an array created
                    if facetype not in cells:
                        cells[facetype] = np.zeros((0, face.get_num_nodes()), dtype=int)
                        cell_data[facetype] = {
                            name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                        }
                    surfnodes = np.array([n.id for n in face.get_nodes()])
                    
                    # add face to the cells
                    cells[facetype] = np.append(cells[facetype], surfnodes.reshape((1,-1)), axis=0)

                    # add surface ids
                    for name in _cell_data_id_names:
                        cell_data[facetype][name] = np.append(cell_data[facetype][name], dsurfid.id)
        
            # go over element edges
            for edge in ele.get_edges():
                # check, whether all nodes of this face belong to a same dline
                union_set = edge.get_dlines()

                # create line cells with id dlineid
                if edge.shape == Line2.ShapeName:
                    linetype = 'line'
                elif edge.shape == Line3.ShapeName:
                    linetype = 'line3'
                else:
                    linetype = None
                
                for dlineid in union_set:
                    # unimplemented face type -> throw error
                    if linetype is None:
                        raise RuntimeError('This kind of edge is not implemented yet! Edge of {0} with {1} nodes'.format(ele.shape, edge.get_num_nodes()))

                    # check, whether there is already an array created
                    if linetype not in cells:
                        cells[linetype] = np.zeros((0, edge.get_num_nodes()), dtype=int)
                        cell_data[linetype] = {
                            name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                        }
                    edgenodes = np.array([n.id for n in edge.get_nodes()])
                    
                    # add edge to the cells
                    cells[linetype] = np.append(cells[linetype], edgenodes.reshape((1, edge.get_num_nodes())), axis=0)

                    # add line ids
                    for name in _cell_data_id_names:
                        cell_data[linetype][name] = np.append(cell_data[linetype][name], dlineid.id)

    
    # store dpoint of every node as extra vertices
    for node in dis.nodes:
        for dp in node.pointnodesets:
            if 'vertex' not in cells:
                cells['vertex'] = np.zeros((0, 1), dtype=int)
                cell_data['vertex'] = {
                    name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                }

            cells['vertex'] = np.append(cells['vertex'], np.reshape(np.array([node.id]), (1,1)), axis=0)
            for name in _cell_data_id_names:
                cell_data['vertex'][name] = np.append(cell_data['vertex'][name], dp.id)


    mesh: meshio.Mesh = meshio.Mesh(points, cells, cell_data=cell_data, point_data=point_data)

    dis.reset()

    return mesh

def _get_id_from_cell_data(celldata):
    for name in _cell_data_id_names:
        if name in celldata:
            return celldata[name]
    
    return None