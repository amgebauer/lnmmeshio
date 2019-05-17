# -*- coding: utf-8 -*-
#
# Maintainer: Martin Pfaller
# slightly adapted from version below
'''
I/O for Gmsh's msh format, cf.
<http://geuz.org/gmsh/doc/texinfo/gmsh.html#File-formats>.

.. moduleauthor:: Nico Schlömer <nico.schloemer@gmail.com>
'''
from itertools import islice

from .common import MeshObject
import numpy as np
import pdb

# dict surface:nodes, e.g.
# {1: array([   1,    3,    4, ..., 9541, 9542, 9543]), 
#  2: array([   2,   133,   134, ..., 15745, 15746, 15747])
#  ...}
def read_surface(cells, cell_tags):
    surface_node_map= {}
    for key in cells:
        # only consider surfaces
        if key == 'triangle' or key == 'quad':
            # loop surface elements
            for (i, element) in enumerate(cells[key]):
                # surface ID of current element
                surf = cell_tags[key][i]
                
                # save node numbers to dict
                if not surf in surface_node_map:
                    surface_node_map[surf] = element
                else:
                    surface_node_map[surf] = np.append(surface_node_map[surf], element)
    # remove duplicate node numbers
    for surf in surface_node_map:
        surface_node_map[surf] = np.unique(surface_node_map[surf])
    
    return surface_node_map

# Read Mesh function
def read(filename):
    # The format is specified at
    # <http://geuz.org/gmsh/doc/texinfo/gmsh.html#MSH-ASCII-file-format>.
    with open(filename) as f:
        while True:
            try:
                line = next(islice(f, 1))
            except StopIteration:
                break
            assert(line[0] == '$')
            environ = line[1:].strip()
            if environ == 'MeshFormat':
                line = next(islice(f, 1))
                # 2.2 0 8
                line = next(islice(f, 1))
                assert(line.strip() == '$EndMeshFormat')
            elif environ == 'Nodes':
                # The first line is the number of nodes
                line = next(islice(f, 1))
                num_nodes = int(line)
                points = np.empty((num_nodes, 3))
                for k, line in enumerate(islice(f, num_nodes)):
                    # Throw away the index immediately
                    points[k, :] = np.array(line.split(), dtype=float)[1:]
                line = next(islice(f, 1))
                assert(line.strip() == '$EndNodes')
            elif environ == 'Elements':
                # The first line is the number of elements
                line = next(islice(f, 1))
                num_cells = int(line)
                cells = {}
                # read tag of element in consequtive order
                cell_tags = {}
                gmsh_to_meshio_type = {
                        15: ('vertex', 1),
                        1: ('line', 2),
                        2: ('triangle', 3),
                        3: ('quad', 4),
                        4: ('tetra', 4),
                        5: ('hexahedron', 8),
                        6: ('wedge', 6)
                        }
                for k, line in enumerate(islice(f, num_cells)):
                    # Throw away the index immediately;
                    data = np.array(line.split(), dtype=int)
                    t = gmsh_to_meshio_type[data[1]]
                    # Subtract one to account for the fact that python indices
                    # are 0-based.
                    if t[0] in cells:
                        cells[t[0]].append(data[-t[1]:] - 1)
                        cell_tags[t[0]].append(data[4])
                    else:
                        cells[t[0]] = [data[-t[1]:] - 1]
                        cell_tags[t[0]] = [data[4]]
    
                line = next(islice(f, 1))
                assert(line.strip() == '$EndElements')
            elif environ == 'PhysicalNames':
                line = next(islice(f, 1))
                num_phys_names = int(line)
                for k, line in enumerate(islice(f, num_phys_names)):
                    pass
                line = next(islice(f, 1))
                assert(line.strip() == '$EndPhysicalNames')
            else:
                raise RuntimeError('Unknown environment \'%s\'.' % environ)

    for key in cells:
        cells[key] = np.vstack(cells[key])
        cell_tags[key] = np.asarray(cell_tags[key], int)
    
    # construct map surface:nodes
    surface_node_map = read_surface(cells, cell_tags)
    
    # initialize empty mesh object
    mesh = MeshObject()
    
    mesh._points = points
    mesh._cells = cells
    mesh._surface_node_map = surface_node_map
    
    # disable, otherwise paraview throws error
#     mesh._cell_tags = cell_tags
#     mesh._cell_data = cell_tags
    
    return mesh


def write(filename, mesh):
    '''Writes msh files, cf.
    http://geuz.org/gmsh/doc/texinfo/gmsh.html#MSH-ASCII-file-format
    '''
    
    with open(filename, 'w') as fh:
        fh.write('$MeshFormat\n2 0 8\n$EndMeshFormat\n')

        # Write nodes
        fh.write('$Nodes\n')
        fh.write('%d\n' % len(mesh._points))
        for k, x in enumerate(mesh._points):
            fh.write('%d %f %f %f\n' % (k+1, x[0], x[1], x[2]))
        fh.write('$EndNodes\n')

        # Translate meshio types to gmsh codes
        # http://geuz.org/gmsh/doc/texinfo/gmsh.html#MSH-ASCII-file-format
        meshio_to_gmsh_type = {
                'vertex': 15,
                'line': 1,
                'triangle': 2,
                'quad': 3,
                'tetra': 4,
                'hexahedron': 5,
                'wedge': 6,
                'tetra10': 11
                }
        
        # write elements
        
        # header
        fh.write('$Elements\n')
        num_cells = 0
        for key, data in mesh._cells.iteritems():
            num_cells += data.shape[0]
        fh.write('%d\n' % num_cells)
        
        # elements
        num_cells = 0
        for key, data in mesh._cells.iteritems():
            n = data.shape[1]
            form = '%d ' + '%d' % meshio_to_gmsh_type[key] + ' 0 ' + \
                ' '.join(n * ['%d']) + '\n'
            for k, c in enumerate(data):
                fh.write(form % ((num_cells+k+1,) + tuple(c + 1)))
            num_cells += data.shape[0]
        fh.write('$EndElements\n')
        
        # node data
        fh.write('$NodeData\n')
        
        # number-of-string-tags
        fh.write('0\n')
        
        # number-of-real-tags
        fh.write('%d\n' % len(mesh._point_data))
        for key, data in mesh._point_data.iteritems():
            fh.write(key='\n')
            for k, c in enumerate(data):
                pdb.set_trace()
                fh.write('%d %f\n' % (k+1, c))
        
        # number-of-integer-tags
        fh.write('%d\n' % len(mesh._surface_node_map))
        
        # export all surfaces
        for key, data in mesh._surface_node_map.iteritems():
            fh.write('surf_'+'%03d\n' % key)
            for c in data:
                fh.write('%d %d\n' % (c+1, 1))
    
        fh.write('$EndNodeData\n')
        
        
    return
