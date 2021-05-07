#
# Maintainer: Amadeus Gebauer
#

import os
import sys
from typing import Union

import numpy as np
from meshio import Mesh
from meshio import read as _meshioread
from meshio import write as _meshiowrite

from . import element, ensightio, ioutils, meshio_to_discretization, mimics_stlio, utils
from .conditions import condition, conditionreader, surf_dirich_condition
from .datfile import Datfile
from .discretization import Discretization
from .element.element import (
    Element,
    Element1D,
    Element2D,
    Element3D,
    ElementHex,
    ElementTet,
)
from .element.element_container import ElementContainer
from .element.hex8 import Hex8
from .element.hex20 import Hex20
from .element.hex27 import Hex27
from .element.line2 import Line2
from .element.line3 import Line3
from .element.quad4 import Quad4
from .element.quad8 import Quad8
from .element.quad9 import Quad9
from .element.tet4 import Tet4
from .element.tet10 import Tet10
from .element.tri3 import Tri3
from .element.tri6 import Tri6
from .fiber import Fiber
from .node import Node
from .nodeset import LineNodeset, PointNodeset, SurfaceNodeset, VolumeNodeset

__TYPE_BACI = 1
__TYPE_BACI_DISCR = 2
__TYPE_CASE = 3
__TYPE_CASE_ASCII = 5
__TYPE_MIMICS_STL = 4
__TYPE_OTHER = 0


def _get_type(filename, file_format=None) -> int:
    if not file_format:
        # deduct file format from extension
        _, extension = os.path.splitext(filename)

        if extension == ".dat":
            return __TYPE_BACI
        elif extension == ".dis":
            return __TYPE_BACI_DISCR
        elif extension == ".case":
            return __TYPE_CASE
        elif extension == ".mstl":
            return __TYPE_MIMICS_STL
    elif file_format == "dat":
        return __TYPE_BACI
    elif file_format == "dis":
        return __TYPE_BACI_DISCR
    elif file_format == "case" or file_format == "ensight":
        return __TYPE_CASE
    elif file_format == "case_ascii":
        return __TYPE_CASE_ASCII
    elif file_format == "mimicsstl":
        return __TYPE_MIMICS_STL

    return __TYPE_OTHER


def read(filename, file_format=None, out=True) -> Datfile:
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

    if ftype == __TYPE_BACI or ftype == __TYPE_BACI_DISCR:
        # this is a BACI file format
        with open(filename, "r") as f:
            return read_baci(f, out=out)
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError("Case file reading is not implemented yet")
    elif ftype == __TYPE_MIMICS_STL:
        dat: Datfile = Datfile()
        dat.discretization = meshio_to_discretization.mesh2Discretization(
            mimics_stlio.read(filename)
        )
        return dat
    else:
        # this maybe is a file format supported by meshio
        dat: Datfile = Datfile()
        dat.discretization = meshio_to_discretization.mesh2Discretization(
            _meshioread(filename, file_format=file_format)
        )
        return dat


def read_discr(filename, file_format=None, out=True):
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

    if ftype == __TYPE_BACI or ftype == __TYPE_BACI_DISCR:
        # this is a BACI file format
        with open(filename, "r") as f:
            return read_baci_discr(f, out=out)
    elif ftype == __TYPE_CASE or ftype == __TYPE_CASE_ASCII:
        # this is ensight gold file format
        raise NotImplementedError("Case file reading is not implemented yet")
    elif ftype == __TYPE_MIMICS_STL:
        dis = meshio_to_discretization.mesh2Discretization(mimics_stlio.read(filename))
        return dis
    else:
        # this maybe is a file format supported by meshio
        dis = meshio_to_discretization.mesh2Discretization(
            _meshioread(filename, file_format=file_format)
        )
        return dis


def read_baci(input_stream, out=True) -> Datfile:
    sections = ioutils.read_dat_sections(input_stream)

    return Datfile.read(sections, out=out)


def read_baci_discr(input_stream, out=True):
    sections = ioutils.read_dat_sections(input_stream)

    return Discretization.read(sections, out=out)


def write(
    filename: str, dat: Datfile, file_format=None, override=True, out=True,
):
    """
    Writes an dat file with head and discretization

    Args:
        filename: The file to read from
        file_format: The file format of the file
        override: Flag, whether existing files should be overriden (dangerous)
    """
    assert isinstance(filename, str)

    if not override and os.path.exists(filename):
        raise FileExistsError("The file already exists")

    ftype: int = _get_type(filename, file_format=file_format)

    if ftype == __TYPE_BACI:
        # this is a BACI file format
        with open(filename, "w") as f:
            dat.write(f, out=out)
    elif ftype == __TYPE_BACI_DISCR:
        # this is a BACI discretization file format
        with open(filename, "w") as f:
            dat.discretization.write(f, out=out)
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        ensightio.write_case(filename, dat, out=out)
    elif ftype == __TYPE_CASE_ASCII:
        # this is ensight gold file format
        ensightio.write_case(filename, dat, out=out, binary=False)
    elif ftype == __TYPE_MIMICS_STL:
        raise NotImplementedError("Writing in Mimics stl is currently not supported")
    else:
        m = meshio_to_discretization.discretization2mesh(dat.discretization)
        write_mesh(filename, m, file_format=file_format)


def write_discr(
    filename: str, dis: Discretization, file_format=None, override=True, out=True
):
    dat: Datfile = Datfile()
    dat.discretization = dis

    write(filename, dat, file_format=file_format, override=override, out=out)


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
        return meshio_to_discretization.discretization2mesh(
            read(filename, file_format=file_format).discretization
        )
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError("Case file reading into mesh is not implemented yet")
    elif ftype == __TYPE_MIMICS_STL:
        return mimics_stlio.read(filename)
    else:
        # this maybe is a file format supported by meshio
        return _meshioread(filename, file_format=file_format)


def write_mesh(filename, mesh, file_format=None, override=True, **kwargs):
    """
    Writes an unstructured mesh with added data from meshio raw data

    Args:
        filename: The file to read from
        mesh: meshio raw mesh data
        file_format: The file format of the file
        override: Flag, whether existing files should be overriden (dangerous)
    """
    assert isinstance(filename, str)

    ftype: int = _get_type(filename, file_format=file_format)

    if not override and os.path.isfile(filename):
        raise FileExistsError("The file already exists")

    if ftype == __TYPE_BACI:
        dat = Datfile()
        dat.discretization = meshio_to_discretization.mesh2Discretization(mesh)
        write(
            filename, dat, file_format=file_format,
        )
    elif ftype == __TYPE_CASE:
        # this is ensight gold file format
        raise NotImplementedError("Case file writing into mesh is not implemented yet")
    elif ftype == __TYPE_MIMICS_STL:
        return mimics_stlio.write(filename, mesh)
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
    with open(filename, "r") as f:
        sections = ioutils.read_dat_sections(f)

    return sections
