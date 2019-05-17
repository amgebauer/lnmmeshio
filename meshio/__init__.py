# -*- coding: utf-8 -*-
#
# Maintainer: Martin Pfaller
# input/output of mesh files
# supported formats: .msh, .dat, .vtu
#
# adapted from meshio 1.7.4 package
# see https://pypi.python.org/pypi/meshio


import sys,os


from . import common
from . import msh_io
from . import vtk_io
from . import dat_io

import numpy as np

input_filetypes = [
        'exodus',
        'gmsh',
        'dolfin-xml',
        'medit',
        'permas',
        'moab',
        'off',
        'vtk',
        'vtu',
        'xdmf',
        'baci'
        ]

output_filetypes = [
        'exodus',
        'gmsh',
        'dolfin-xml',
        'medit',
        'permas',
        'moab',
        'off',
        'vtk-ascii',
        'vtk-binary',
        'vtu',
        'xdmf',
        'baci'
        ]

_extension_to_filetype = {
    '.e': 'exodus',
    '.ex2': 'exodus',
    '.exo': 'exodus',
    '.mesh': 'medit',
    '.msh': 'gmsh',
    '.xml': 'dolfin-xml',
    '.post': 'permas',
    '.post.gz': 'permas',
    '.dato': 'permas',
    '.dato.gz': 'permas',
    '.h5m': 'moab',
    '.off': 'off',
    '.vtu': 'vtu',
    '.vtk': 'vtk',
    '.xdmf': 'xdmf',
    '.xmf': 'xdmf',
    '.dat': 'baci'
    }


def read(filename, file_format=None):
    '''Reads an unstructured mesh with added data.

    :param filenames: The files to read from.
    :type filenames: str
    :returns mesh{2,3}d: The mesh data.
    :returns point_data: Point data read from file.
    :type point_data: dict
    :returns field_data: Field data read from file.
    :type field_data: dict
    '''

    # http://stackoverflow.com/questions/4843173/how-to-check-if-a-type-of-variable-is-string-in-python
    assert isinstance(filename, str)

    if not file_format:
        # deduct file format from extension
        _, extension = os.path.splitext(filename)
        file_format = _extension_to_filetype[extension]

    if file_format == 'gmsh':
        return msh_io.read(filename)
#     elif file_format == 'medit':
#         return medit_io.read(filename)
#     elif file_format == 'dolfin-xml':
#         return dolfin_io.read(filename)
#     elif file_format == 'permas':
#         return permas_io.read(filename)
#     elif file_format == 'moab':
#         return h5m_io.read(filename)
#     elif file_format == 'off':
#         return off_io.read(filename)
    elif file_format == 'vtu':
        return vtk_io.read('vtu', filename)
    elif file_format == 'vtk':
        return vtk_io.read('vtk', filename)
    elif file_format == 'xdmf':
        return vtk_io.read('xdmf', filename)
    elif file_format == 'exodus':
        return vtk_io.read('exodus', filename)
    elif file_format == 'baci':
        return dat_io.read(filename)
    else:
        raise RuntimeError(
            'Unknown file format \'%s\' of file \'%s\'.' %
            (file_format, filename)
            )


def write(filename, mesh):
    '''Writes mesh together with data to a file.

    :params filename: File to write to.
    :type filename: str

    :params point_data: Named additional point data to write to the file.
    :type point_data: dict
    '''

#     if not file_format:
    # deduct file format from extension
    _, extension = os.path.splitext(filename)
    file_format = _extension_to_filetype[extension]

    cells = mesh._cells
    
    # check cells for sanity
    if 'vertex' in cells:
        assert cells['vertex'].shape[1] == 1
    if 'line' in cells:
        assert cells['line'].shape[1] == 2
    if 'triangle' in cells:
        assert cells['triangle'].shape[1] == 3
    if 'quad' in cells:
        assert cells['quad'].shape[1] == 4
    if 'tetra' in cells:
        assert cells['tetra'].shape[1] == 4
    if 'tetra10' in cells:
        assert cells['tetra10'].shape[1] == 10
    if 'hexahedron' in cells:
        assert cells['hexahedron'].shape[1] == 8
    if 'wedge' in cells:
        assert cells['wedge'].shape[1] == 6
    if 'pyramid' in cells:
        assert cells['pyramid'].shape[1] == 5

#     if file_format == 'moab':
#         h5m_io.write(
#             filename, points, cells,
#             point_data=point_data,
#             cell_data=cell_data,
#             field_data=field_data
#             )
#     elif file_format == 'medit':
#         medit_io.write(filename, points, cells)
#     elif file_format == 'dolfin-xml':
#         dolfin_io.write(filename, points, cells)
#     elif file_format == 'off':
#         off_io.write(filename, points, cells)
#     elif file_format == 'permas':
#         permas_io.write(filename, points, cells)
#     elif file_format in ['vtk', 'vtk-ascii']:
#         vtk_io.write(
#             'vtk-ascii', filename,
#             points, cells,
#             point_data=point_data,
#             cell_data=cell_data,
#             field_data=field_data
#             )
#     elif file_format == 'vtk-binary':
#         vtk_io.write(
#             'vtk-binary', filename,
#             points, cells,
#             point_data=point_data,
#             cell_data=cell_data,
#             field_data=field_data
#             )
#     elif file_format == 'xdmf':  # XDMF
#         vtk_io.write(
#             'xdmf', filename, points, cells,
#             point_data=point_data,
#             cell_data=cell_data,
#             field_data=field_data
#             )
#     elif file_format == 'exodus':  # exodus ii format
#         vtk_io.write(
#             'exodus', filename, points, cells,
#             point_data=point_data,
#             cell_data=cell_data,
#             field_data=field_data
#             )
    if file_format == 'gmsh':
        msh_io.write(filename, mesh)
    elif file_format == 'baci':
        dat_io.write(filename, mesh)
    elif file_format == 'vtu':  # vtk xml format
        vtk_io.write('vtu', filename, mesh)
    else:
        raise RuntimeError(
            'unknown file format \'%s\' of \'%s\'.' % (file_format, filename)
            )
    return