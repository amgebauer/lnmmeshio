#
# Maintainer: Amadeus Gebauer
#

import sys,os

from meshio import Mesh, read as _meshioread, write as _meshiowrite
from . import meshio_to_discretization
from .discretization import Element, Discretization, Node
from . import ioutils

import numpy as np

def _is_baci(filename, file_format=None) -> bool:
    if not file_format:
        # deduct file format from extension
        _, extension = os.path.splitext(filename)

        if extension == '.dat' or extension == '.dis':
            return True
    elif file_format == 'dat' or file_format == 'dis':
        return True
    
    return False

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

    is_baci: bool = _is_baci(filename, file_format=file_format)

    if is_baci:
        # this is a BACI file format
        with open(filename, 'r') as f:
            return read_baci(f)
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

    is_baci: bool = _is_baci(filename, file_format=file_format)

    if is_baci:
        # this is a BACI file format
        with open(filename, 'w') as f:
            discretization.write(f)

    else:
        print('This branch is experimental. Please double check the result!')
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

    is_baci: bool = _is_baci(filename, file_format=file_format)

    if is_baci:
        # this is a BACI file format
        print('This branch is experimental. Please double check the result!')
        return meshio_to_discretization.discretization2mesh(read(filename, file_format=file_format))
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

    is_baci: bool = _is_baci(filename, file_format=file_format)

    if is_baci:
        write(filename, meshio_to_discretization.mesh2Discretization(mesh), file_format=file_format)

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