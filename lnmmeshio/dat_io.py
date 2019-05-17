# -*- coding: utf-8 -*-
#
# Maintainer: Martin Pfaller

import pdb
import numpy as np
from .common import MeshObject, get_etype

from .read_ccarat import read_ccarat, write_ccarat
from .elements import readnodes, bcdictionary, collect_all_bc_top_nodes, elementtypes, surfaces
from .elements import surfaces as ele_surf_def


ele_dic = {'FIBER1':'elefiber1',
           'FIBER2':'elefiber2',
           'FIBER3':'elefiber3'}

node_dic = {'FIBER1':'nodfiber1',
            'FIBER2':'nodfiber2',
            'FIBER3':'nodfiber3'}

# add line to key in dic
def add(d,k,l):
    if k in d:
        d[k].append(l)
    else:
        d[k] = [l]
    return

# find value of scalar quantity q in list l
def find_val(l,q):
    try:
        i = l.index(q)
        return int(l[i+1])
    except ValueError:
        return 0

# find value of vector q in list l
def find_vec(l,q):
    try:
        i = l.index(q)
        return [float(v) for v in l[i+1:i+4]]
    except ValueError:
        return [0.0, 0.0, 0.0]

# convert dic entries to numpy arrays 
def to_np(a):
    for k,v in a.items():
        a[k] = np.array(v)

# Read Mesh function
def read(filename):
    section_names, sections = read_ccarat(filename)
    _, _, nodemap, fiber1, fiber2 = readnodes(sections)
    _, _, surface_node_map, _ = bcdictionary(sections) 
    
    # process geometry
    if 'STRUCTURE ELEMENTS' in sections and sections['STRUCTURE ELEMENTS']:
        used_section = sections['STRUCTURE ELEMENTS']
    elif 'TRANSPORT ELEMENTS' in sections and sections['TRANSPORT ELEMENTS']:
        used_section = sections['TRANSPORT ELEMENTS']
    
    # initialize empty mesh object
    mesh = MeshObject()
    
    # coordinates
    mesh._points = np.asarray(list(nodemap.values()))
    
    if fiber1:
        mesh._point_data['fiber1'] = np.asarray(fiber1)
    if fiber2:
        mesh._point_data['fiber2'] = np.asarray(fiber2)
    
    # elements ()
    n_ele = len(used_section)
#     mesh._cell_data['material'] = np.zeros(n_ele, dtype=int)
    
    for e in used_section:
        id = int(e[0])-1
        type = e[2]
        
        # subtract 1 from node IDs since python indexing starts at 0
        nodes = [int(n)-1 for n in e[3:3+elementtypes[type]]]
        
        # add element
        add(mesh._cells,get_etype(type),nodes)
        
#         # add material
#         mesh._cell_data['material'][id] = find_val(e,'MAT')
#         
#         # add fibers
#         for f,g in ele_dic.iteritems():
#             add(mesh._cell_data,g,find_vec(e,f))
    
    to_np(mesh._cells)

    
    # convert each TET10 to 8 TET4
    if 'tetra10' in mesh._cells:
        # list of node IDs of TET4 within TET10
        tets = [[0,4,6,7],
                [4,1,5,8],
                [6,5,2,9],
                [7,8,9,3],
                [7,8,6,9],
                [6,8,5,9],
                [7,4,6,8],
                [8,4,6,5]]
        
        mesh._cells['tetra'] = np.append(mesh._cells['tetra'],
            np.vstack([np.column_stack([mesh._cells['tetra10'][:,i] for i in t]) for t in tets]),
            axis=0)
        
        del mesh._cells['tetra10']

    # dict surface:nodes
    mesh._surface_node_map = {key:np.asarray(list(value))-1 for key, value in surface_node_map.items()}
    

    # create triangle elements on surface
    # loop all 4 surface triangles of each tet
    if 'tetra' in mesh._cells:
        
        # surface node oredring
        ele_surf = np.asarray(ele_surf_def['TET4'])
    
        # reverse order so that it matches the definition of meshio
        ele_surf[:,[1,2]] = ele_surf[:,[2,1]]
        
        nodes = np.empty((0,3), int)
        for surfaces in ele_surf:
            # loop all nodes of each surface triangle
            surf = np.zeros([len(mesh._cells['tetra']),3])
            for i,s in enumerate(surfaces):
                surf[:,i] = mesh._cells['tetra'][:,s]
            nodes = np.append(nodes, surf, axis=0)
    
        # list of sorted nodes
        nodes_sorted = nodes.copy()
        nodes_sorted.sort()
        
        # dict of index in nodes of unique triangles
        from collections import OrderedDict
        unique_nodes = OrderedDict()
        for (i,n) in enumerate(nodes_sorted):
            t = tuple(n)
            if t in unique_nodes:
                # store only triangles who occur once -> surface triangles
                del unique_nodes[t]
            else:
                # save index of triangle
                unique_nodes[t] = i
    
        new_tri = np.asarray(nodes[list(unique_nodes.values())], int)
        if 'triangle' in mesh._cells:
            mesh._cells['triangle'] = np.append(mesh._cells['triangle'], new_tri)
        else:
            mesh._cells['triangle'] = new_tri
    
    # safety check
    if 'hexahedron' in mesh._cells:
        print('WARNING: HEX elements are not properly implemented yet! Be careful!')
    
    # store for output
    mesh._section_names = section_names
    mesh._sections = sections

    return mesh


def write(filename, mesh):
    # TODO: implement export to .dat-file from arbitrary input
    if not hasattr(mesh, '_sections'):
        RuntimeError('You can only export .dat files if the input is .dat')
    
    # default: write cir,tan basis vectors and helix,transverse angles to nodes
    if 'angle_helix' in mesh._point_data:
        # loop all nodes
        for i,line in enumerate(mesh._sections['NODE COORDS']):
            line[0] = 'FNODE'
            line += ['CIR'] + [repr(mesh._point_data['basis_cir'][i,j]) for j in range(3)]
            line += ['TAN'] + [repr(mesh._point_data['basis_tan'][i,j]) for j in range(3)]
            line += ['HELIX'] + [repr(mesh._point_data['angle_helix'][i])]
            line += ['TRANS'] + [repr(mesh._point_data['angle_trans'][i])]
        
    # write fiber vector if exists
#    elif 'vector_fiber' in mesh._point_data:
#        for line, b in zip(mesh._sections['NODE COORDS'], mesh._point_data['vector_fiber']):
#            line[0] = 'FNODE'
#            line += ['FIBER1'] + [repr(b[i]) for i in range(3)]
    
    # write orthonormal basis as nodal fiber orientations if exists (only if no fiber vector present)
    elif 'basis_cir' in mesh._point_data:
        basis = np.hstack((mesh._point_data['basis_cir'],
                           mesh._point_data['basis_tan'],
                           mesh._point_data['basis_rad']))
         
        # loop all nodes
        for line, b in zip(mesh._sections['NODE COORDS'], basis):
            # loop all 3 basis vectors
            for f in range(3):
                # add basis vectors to node
                line += ['FIBER' + repr(f+1)] + [repr(b[i]) for i in range(3*f,3*(f+1))]
    for id,a in enumerate(['helix', 'sheet']):
        if ('vector_' + a) in mesh._point_data:
            # loop all nodes
            for line, b in zip(mesh._sections['NODE COORDS'], mesh._point_data['vector_' + a]):
                line[0] = 'FNODE'
                # add basis vectors to node
                line += ['FIBER' + repr(id+1)] + [repr(b[i]) for i in range(3)]
     
 #   # write manifold system if exists
 #   if 'mani_cir' in mesh._point_data:
 #       mani = np.vstack((mesh._point_data['mani_axi'],
 #                         mesh._point_data['mani_cir'])).T
 #        
 #       names = ['lin_axial', 'lin_cir']
 #        
 #       # loop all nodes
 #       for line, b in zip(mesh._sections['DSURF-NODE TOPOLOGY'], mani):
 #           # loop all 3 basis vectors
 #           for i in range(len(names)):
 #               # add basis vectors to node
 #               line += [names[i]] + [repr(b[i])]
 #        
 #       for line, b in zip(mesh._sections['NODE COORDS'], mesh._point_data['mani_trans']):
 #           line += ['transmural'] + [repr(b)]
 #   
    write_ccarat(filename, mesh._section_names, mesh._sections)
    return