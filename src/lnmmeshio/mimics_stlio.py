"""
This file is mainly based on the stl-reader by meshio (https://github.com/nschloe/meshio).

Copyright (c) 2015-2021 Nico Schlömer et al.

I/O for the STL format, cf.
<https://en.wikipedia.org/wiki/STL_(file_format)>.
"""
import io
import logging
import struct

import numpy
from meshio import Mesh


def read(filename):
    """Reads a Gmsh msh file."""
    with open(filename, "rb") as f:
        out = read_buffer(f)
    return out


def read_buffer(f):
    data = numpy.frombuffer(f.read(5), dtype=numpy.uint8)
    if "".join([chr(item) for item in data]) == "solid":
        raise RuntimeError(
            "This is the Mimics stl format, which should be binary, not ascii"
        )

    # binary: read and discard 75 more bytes
    f.read(75)
    return _read_binary(f)


def data_from_facets(facets):
    # Now, all facets contain the point coordinate. Try to identify individual
    # points and build the data arrays.
    pts = numpy.concatenate(facets)

    # TODO equip `unique()` with a tolerance
    # Use return_index so we can use sort on `idx` such that the order is
    # preserved; see <https://stackoverflow.com/a/15637512/353337>.
    _, idx, inv = numpy.unique(pts, axis=0, return_index=True, return_inverse=True)
    k = numpy.argsort(idx)
    points = pts[idx[k]]
    inv_k = numpy.argsort(k)
    cells = [("triangle", inv_k[inv].reshape(-1, 3))]
    return points, cells


def _read_binary(f):
    # read the first uint32 byte to get the number of triangles
    data = numpy.frombuffer(f.read(4), dtype=numpy.uint32)
    num_triangles = data[0]

    facets = []
    facet_data = []
    for _ in range(num_triangles):
        # discard the normal
        f.read(12)
        facets.append(numpy.frombuffer(f.read(36), dtype=numpy.float32).reshape(-1, 3))
        # discard the attribute byte count
        facet_data.append(int(struct.unpack("<h", f.read(2))[0]))

    points, cells = data_from_facets(numpy.array(facets))

    cell_data = {"medit:ref": [numpy.array(facet_data)]}
    return Mesh(points, cells, cell_data=cell_data)


def write(filename, mesh):
    assert (
        len(mesh.cells) == 1 and mesh.cells[0].type == "triangle"
    ), "STL can only write triangle cells."

    if mesh.points.shape[1] == 2:
        logging.warning(
            "STL requires 3D points, but 2D points given. "
            "Appending 0 third component."
        )
        mesh.points = numpy.column_stack(
            [mesh.points[:, 0], mesh.points[:, 1], numpy.zeros(mesh.points.shape[0])]
        )

    _write_binary(filename, mesh.points, mesh.cells, cell_data=mesh.cell_data)

    return


def _compute_normals(pts):
    normals = numpy.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
    nrm = numpy.sqrt(numpy.einsum("ij,ij->i", normals, normals))
    normals = (normals.T / nrm).T
    return normals


def _write_binary(filename, points, cells, cell_data=None):
    pts = None
    attrs = None
    for i, t in enumerate(cells):
        if t.type == "triangle":
            pts = points[t.data]

            if cell_data is not None and "medit:ref" in cell_data:
                attrs = cell_data["medit:ref"][i].astype(numpy.uint16)
            break

    if pts is None:
        raise RuntimeError("Could not find triangled")

    if attrs is None:
        attrs = numpy.zeros((len(pts)), dtype=numpy.uint16)

    normals = _compute_normals(pts)

    with open(filename, "wb") as fh:
        # 80 character header data containing default color for 3-matic
        byte_io = io.BytesIO()
        byte_io.write(
            b"COLOR=\xc0\xc0\xc0\x00,MATERIAL=\x80\x80\x80\xff\x80\x80\x80\xff\x00\x00\x00\xff\x00\x00\xa0A;SOLID\x00"
        )
        byte_io.write(b" " * (80 - byte_io.getbuffer().nbytes))

        fh.write(byte_io.getbuffer().tobytes())
        fh.write(numpy.uint32(len(cells[0].data)))
        for pt, normal, attr in zip(pts, normals, attrs):
            fh.write(normal.astype(numpy.float32))
            fh.write(pt.astype(numpy.float32))
            fh.write(attr)

    return
