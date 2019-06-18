#
# Maintainer: Amadeus Gebauer
#

import sys,os

from meshio import Mesh, read as _meshioread, write as _meshiowrite
from . import meshio_to_discretization
from .discretization import Discretization
from .node import Node
from .fiber import Fiber
from .element.element import Element
from .element.hex8 import Hex8
from .element.tet10 import Tet10
from .element.tet4 import Tet4
from .element.quad4 import Quad4
from .element.tri6 import Tri6
from .element.tri3 import Tri3
from .element.line2 import Line2
from .element.line3 import Line3
from . import ioutils
from . import ensightio

import numpy as np

__TYPE_BACI = 1
__TYPE_CASE = 2
__TYPE_OTHER = 0

def _get_type(filename, file_format=None) -> bool:
    if not file_format:
        # deduct file format from extension
        _, extension = os.path.splitext(filename)

        if extension == '.dat' or extension == '.dis':
            return __TYPE_BACI
        elif extension == '.case':
            return __TYPE_CASE
    elif file_format == 'dat' or file_format == 'dis':
        return __TYPE_BACI
    elif file_format == 'case' or file_format == 'ensight':
        return __TYPE_CASE
    
    return __TYPE_OTHER

def read(filename, file_format=None):
    """
    Reads an unstructured mesh with added data

    Args:
        filename: The file to read from
        file_format: The file format of the file
    
    Returns:
        Discretization: Returns the discretization in BACI format
    """
    assert isinstance(filename, str)

    ftype: int = _get_type(filename, file_format=file_format)

    if ftype == __TYPE_BACI:
        # this is a BACI file format
        with open(filename, 'r') as f:
            return read_baci(f)
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError('Case file reading is not implemented yet')
    else:
        # this maybe is a file format supported by meshio
        return meshio_to_discretization.mesh2Discretization(
            _meshioread(filename, file_format=file_format)
        )

def read_baci(input_stream):
    sections = ioutils.read_dat_sections(input_stream)
                
    return Discretization.read(sections)

def write(filename: str, discretization: Discretization, file_format=None):
    """
    Writes an unstructured mesh with added data

    Args:
        filename: The file to read from
        file_format: The file format of the file
    
    Returns:
        Discretization: Returns the discretization in BACI format
    """
    assert isinstance(filename, str)

    ftype: int = _get_type(filename, file_format=file_format)

    if ftype == __TYPE_BACI:
        # this is a BACI file format
        with open(filename, 'w') as f:
            discretization.write(f)
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        ensightio.write_case(filename, discretization)
    else:
        write_mesh(filename, meshio_to_discretization.discretization2mesh(discretization), file_format=file_format)

def read_mesh(filename, file_format=None):
    """
    Reads an unstructured mesh with added data into the meshio raw format

    Args:
        filename: The file to read from
        file_format: The file format of the file
    
    Returns:
        Mesh: Returns the discretization in BACI format
    """
    assert isinstance(filename, str)

    ftype: int = _get_type(filename, file_format=file_format)

    if ftype == __TYPE_BACI:
        # this is a BACI file format
        return meshio_to_discretization.discretization2mesh(read(filename, file_format=file_format))
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError('Case file reading into mesh is not implemented yet')
    else:
        # this maybe is a file format supported by meshio
        return _meshioread(filename, file_format=file_format)

def write_mesh(filename, mesh, file_format=None, **kwargs):
    """
    Writes an unstructured mesh with added data from meshio raw data

    Args:
        filename: The file to read from
        mesh: meshio raw mesh data
        file_format: The file format of the file
    """
    assert isinstance(filename, str)

    ftype: int = _get_type(filename, file_format=file_format)

    if ftype == __TYPE_BACI:
        write(filename, meshio_to_discretization.mesh2Discretization(mesh), file_format=file_format)
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError('Case file writing into mesh is not implemented yet')
    else:
        _meshiowrite(filename, mesh, file_format, **kwargs)

def read_sections(filename):
    """
    Reads the sections of a dat file and returns a dictionary with the section title as key and the
    lines as an array

    Args:
        filename: Path to the datfile
    
    Returns:
        dict: keys are the section names and value is a list of the lines
    """
    with open(filename, 'r') as f:
        sections = ioutils.read_dat_sections(f)

    return sections