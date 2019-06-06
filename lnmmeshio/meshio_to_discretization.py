# 
# Maintainer: Amadeus Gebauer
# 
# This is the interface between the meshio package and our Discretization description
# May not work perfectly
# 
import numpy as np
import meshio
from .discretization import Element, Discretization, Node
from progress.bar import Bar

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
    for i, coord in Bar('Create nodes').iter(enumerate(mesh.points)):
        n = Node(coord)

        for key, v in mesh.point_data.items():
            n.data[key] = v[i]

        disc.nodes.append(
            n
        )

    # get the maximum element dimension, which is the dimension of the mesh
    maxdim = max([cell_to_dim[celltype] for celltype in mesh.cells.keys()])
    
    # create Elements from cells
    disc.elements[Element.FieldTypeStructure] = []
    for celltype, cells in Bar('Create elements').iter(mesh.cells.items()):

        if celltype not in cell_nodes:
            raise Exception('The cell type {0} is currently not implemented'.format(celltype))
        
        cellindex: int = 0
        for cell in cells:
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
                ele = Element(
                    cell_disc_eles[celltype],
                    cell_disc_shape[celltype],
                    # also need to reorder nodes in a few element types
                    [nodes[i] for i in ele_node_order_vtk2baci[cell_disc_shape[celltype]]]
                )
                disc.elements[Element.FieldTypeStructure].append(ele)

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
                        if nsid not in node.dpoint:
                            node.dpoint.append(nsid)
                    elif eledim == 1:
                        if nsid not in node.dline:
                            node.dline.append(nsid)
                    elif eledim == 2:
                        if nsid not in node.dsurf:
                            node.dsurf.append(nsid)
            
            cellindex += 1



    # copy element data
    for celltype, cells in mesh.cells.items():
        pass
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

            for key, value in ele.data:
                if key not in cell_data[celltype]:
                    cell_data[celltype][key] = value.reshape(tuple([1]+list(value.shape)))
                else:
                    cell_data[celltype][key] = np.append(cell_data[celltype][key], value.reshape(tuple([1]+list(value.shape))), axis=0)

            # store material id
            if 'MAT' in ele.options:
                for name in _cell_data_id_names:
                    cell_data[celltype][name] = np.append(cell_data[celltype][name], int(ele.options['MAT'][0]))
            
            # go over element faces
            for face in Element.ElementFaces[ele.shape]:
                # check, whether all nodes of this face belong to a same dline
                union_set = None
                for nodepos in face:
                    if union_set is None:
                        union_set = set(ele.nodes[nodepos].dsurf)
                    else:
                        union_set = union_set.intersection(set(ele.nodes[nodepos].dsurf))
                
                for dsurfid in union_set:
                    # create surface cells with id dsurfid
                    facetype: str = None
                    if len(face) == 3 and ele.shape == 'TET4':
                        # create triangle
                        facetype: str = 'triangle'
                    elif len(face) == 6 and ele.shape == 'TET10':
                        # create triangle6
                        facetype: str = 'triangle6'
                    elif len(face) == 4 and ele.shape == 'HEX8':
                        # create triangle6
                        facetype: str = 'quad'
                    elif len(face) == 9 and (ele.shape == 'HEX27' or ele.shape == 'HEX20'):
                        # create triangle6
                        facetype: str = 'quad9'

                    # unimolemented face type -> throw error
                    if facetype is None:
                        raise RuntimeError('This kind of face is not implemented yet! Face of {0} with {1} nodes'.format(ele.shape, len(face)))

                    # check, whether there is already an array created
                    if facetype not in cells:
                        cells[facetype] = np.zeros((0, len(face)), dtype=int)
                        cell_data[facetype] = {
                            name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                        }
                    surfnodes = np.array([ele.nodes[n].id for n in face])
                    
                    # add face to the cells
                    cells[facetype] = np.append(cells[facetype], surfnodes.reshape((1,-1)), axis=0)

                    # add surface ids
                    for name in _cell_data_id_names:
                        cell_data[facetype][name] = np.append(cell_data[facetype][name], dsurfid)
        
            # go over element edges
            for edge in Element.ElementEdges[ele.shape]:
                # check, whether all nodes of this face belong to a same dline
                union_set = None
                for nodepos in edge:
                    if union_set is None:
                        union_set = set(ele.nodes[nodepos].dline)
                    else:
                        union_set = union_set.intersection(set(ele.nodes[nodepos].dline))
                
                for dlineid in union_set:
                    # create line cells with id dlineid
                    linetype: str = None
                    if len(edge) == 2 and ele.shape == 'TET4':
                        # create line
                        linetype: str = 'line'
                    elif len(edge) == 3 and ele.shape == 'TET10':
                        # create triangle6
                        linetype: str = 'line3'
                    elif len(edge) == 2 and ele.shape == 'HEX8':
                        # create line
                        linetype: str = 'line'
                    elif len(edge) == 3 and (ele.shape == 'HEX27' or ele.shape == 'HEX20'):
                        # create line3
                        linetype: str = 'line3'

                    # unimolemented face type -> throw error
                    if linetype is None:
                        raise RuntimeError('This kind of edge is not implemented yet! Edge of {0} with {1} nodes'.format(ele.shape, len(edge)))

                    # check, whether there is already an array created
                    if linetype not in cells:
                        cells[linetype] = np.zeros((0, len(edge)), dtype=int)
                        cell_data[linetype] = {
                            name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                        }
                    edgenodes = np.array([ele.nodes[n].id for n in edge])
                    
                    # add edge to the cells
                    cells[linetype] = np.append(cells[linetype], edgenodes.reshape((1, len(edge))), axis=0)

                    # add line ids
                    for name in _cell_data_id_names:
                        cell_data[linetype][name] = np.append(cell_data[linetype][name], dlineid)

    
    # store dpoint of every node as extra vertices
    for node in dis.nodes:
        for dp in node.dpoint:
            if 'vertex' not in cells:
                cells['vertex'] = np.zeros((0, 1), dtype=int)
                cell_data['vertex'] = {
                    name: np.zeros((0), dtype=int) for name in _cell_data_id_names
                }

            cells['vertex'] = np.append(cells['vertex'], node.id)
            for name in _cell_data_id_names:
                cell_data['vertex'][name] = np.append(cell_data[celltype][name], dp)


    mesh: meshio.Mesh = meshio.Mesh(points, cells, cell_data=cell_data, point_data=point_data)

    dis.reset()

    return mesh

def _get_id_from_cell_data(celldata):
    for name in _cell_data_id_names:
        if name in celldata:
            return celldata[name]
    
    return None