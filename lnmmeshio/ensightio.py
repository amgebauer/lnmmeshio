import os
from typing import IO, Any, Dict, List, Tuple

import numpy as np

from . import ioutils as io
from .discretization import Discretization
from .progress import progress

shape_to_eletype: Dict[str, str] = {
    "TET4": "tetra4",
    "TET10": "tetra10",
    "HEX8": "hexa8",
    "HEX20": "hexa20",
    "HEX27": "hexa27",
    "QUAD4": "quad4",
    "TRI3": "tria3",
    "LINE2": "bar2",
}


def get_unique_filename(filename: str) -> str:
    splitted = os.path.splitext(filename)

    # write geometry file
    fname = "{0}{1}".format(splitted[0], splitted[1])
    i = 1
    while os.path.exists(fname):
        fname = "{0}-{1}{2}".format(splitted[0], i, splitted[1])
        i += 1

    return fname


def write_case(
    filename,
    dis: Discretization,
    binary: bool = True,
    override: bool = False,
    out: bool = True,
) -> None:
    dis.compute_ids(False)
    filedir = os.path.dirname(filename)

    basename = os.path.splitext(os.path.basename(filedir))[0]

    # write geometry file
    if override:
        geofile = os.path.join(filedir, "{0}_geometry.geo".format(basename))
    else:
        geofile = get_unique_filename(
            os.path.join(filedir, "{0}_geometry.geo".format(basename))
        )

    with open(geofile, "w{0}".format("b" if binary else "")) as f:
        write_geometry(f, dis, binary=binary, out=out)

    # A variable is supposed to be transient if len(shape) == 3 (time component is first index)
    # write element variables
    ele_count = {}
    # get number of elements for each type
    for eles in dis.elements.values():
        for ele in eles:
            if ele.shape not in shape_to_eletype:
                raise NotImplementedError(
                    "This kind of element is not known: {0}".format(ele.shape)
                )
            eletype = shape_to_eletype[ele.shape]

            if eletype not in ele_count:
                ele_count[eletype] = 0

            ele_count[eletype] += 1

    # build element variables
    ele_vars = {}
    ele_cur_count = {}
    for eles in progress(dis.elements.values(), out=out, label="Prepare element data"):
        for ele in eles:
            if ele.shape not in shape_to_eletype:
                raise NotImplementedError(
                    "This kind of element is not known: {0}".format(ele.shape)
                )
            eletype = shape_to_eletype[ele.shape]

            if eletype not in ele_cur_count:
                ele_cur_count[eletype] = 0

            for varname, data in ele.data.items():
                data = np.array(data)
                if len(data.shape) == 0:
                    data = data.reshape((1))

                if varname not in ele_vars:
                    ele_vars[varname] = {}
                    for elt, eltc in ele_count.items():
                        ele_vars[varname][elt] = np.zeros(
                            tuple([eltc] + list(data.shape)), dtype=data.dtype
                        )

                ele_vars[varname][eletype][ele_cur_count[eletype]] = data

            ele_cur_count[eletype] += 1

    # write them finally
    ele_vars_props = {}
    for varname, data in progress(
        ele_vars.items(), out=out, label="Write element data"
    ):
        if override:
            varfile = os.path.join(
                filedir, "{0}_variable.{1}".format(basename, varname)
            )
        else:
            varfile = get_unique_filename(
                os.path.join(filedir, "{0}_variable.{1}".format(basename, varname))
            )
        ele_vars_props[varname] = {}
        ele_vars_props[varname]["filename"] = os.path.basename(varfile)
        with open(varfile, "w{0}".format("b" if binary else "")) as f:
            (
                ele_vars_props[varname]["timesteps"],
                ele_vars_props[varname]["dim"],
            ) = write_element_variable(f, dis, varname, data, binary=binary)

    # write nodal variables
    nodal_vars = {}
    for i, node in progress(enumerate(dis.nodes), out=out, label="Prepare nodal data"):
        for varname, data in node.data.items():
            # ensure that data is a np array
            data = np.array(data)
            if len(data.shape) == 0:
                data = data.reshape((1))
            if varname not in nodal_vars:
                nodal_vars[varname] = np.zeros(
                    tuple([len(dis.nodes)] + list(data.shape)),
                    dtype=data.dtype,
                )

            nodal_vars[varname][i] = data

    nodal_vars_props = {}
    for varname, data in progress(
        nodal_vars.items(), out=out, label="Write nodal data"
    ):
        if override:
            varfile = os.path.join(
                filedir, "{0}_variable.{1}".format(basename, varname)
            )
        else:
            varfile = get_unique_filename(
                os.path.join(filedir, "{0}_variable.{1}".format(basename, varname))
            )
        nodal_vars_props[varname] = {}
        nodal_vars_props[varname]["filename"] = os.path.basename(varfile)
        with open(varfile, "w{0}".format("b" if binary else "")) as f:
            (
                nodal_vars_props[varname]["timesteps"],
                nodal_vars_props[varname]["dim"],
            ) = write_node_variable(f, dis, varname, data, binary=binary)

    # write case file
    if override:
        casefile = filename
    else:
        casefile = get_unique_filename(filename)
    with open(casefile, "w") as f:
        _write_case(f, os.path.basename(geofile), ele_vars_props, nodal_vars_props)


def _write_case(
    fstream: IO,
    geofile: str,
    ele_vars_props: Dict[str, Dict[str, Any]],
    nodal_vars_props: Dict[str, Dict[str, Any]],
) -> None:
    sets = {1: 1}
    dim_to_type = {1: "scalar", 3: "vector", 6: "tensor symm"}

    nextset = 2
    for prop in ele_vars_props.values():
        if prop["timesteps"] not in sets:
            sets[prop["timesteps"]] = nextset
            nextset += 1

    for prop in nodal_vars_props.values():
        if prop["timesteps"] not in sets:
            sets[prop["timesteps"]] = nextset
            nextset += 1

    fstream.write("FORMAT\n\ntype:\tensight gold\n\n")
    fstream.write("GEOMETRY\n\n")
    fstream.write("model:\t{0}\t{1}\t{2}\n\n\n".format(sets[1], sets[1], geofile))
    fstream.write("VARIABLE\n\n")
    # Todo variables
    for varname, props in ele_vars_props.items():
        if props["dim"] not in dim_to_type:
            continue
        fstream.write(
            "{0} per {1}:\t{2}\t{3}\t{4}\t{5}\n".format(
                dim_to_type[props["dim"]],
                "element",
                sets[props["timesteps"]],
                sets[props["timesteps"]],
                varname,
                props["filename"],
            )
        )

    for varname, props in nodal_vars_props.items():
        if props["dim"] not in dim_to_type:
            continue
        fstream.write(
            "{0} per {1}:\t{2}\t{3}\t{4}\t{5}\n".format(
                dim_to_type[props["dim"]],
                "node",
                sets[props["timesteps"]],
                sets[props["timesteps"]],
                varname,
                props["filename"],
            )
        )

    fstream.write("\n")
    fstream.write("TIME\n\n")
    for id, count in sets.items():
        fstream.write(get_timeset_entry(id, count))
        fstream.write("\n")

    fstream.write("\n")
    fstream.write("FILE\n\n")
    for id, count in sets.items():
        fstream.write("file set:\t\t{0}\nnumber of steps:\t\t{1}\n".format(id, count))
    fstream.write("\n")


def get_timeset_entry(id, count):
    entry: str = "time set:\t\t{0}\nnumber of steps:\t\t{1}\ntime values: ".format(
        id, count
    )

    i: int = 0
    for item in range(count):
        if i > 0 and i % 8 == 0:
            entry += "\n"

        entry += " {0}".format(float(item))

        i += 1

    return entry


def write_geometry(
    fstream: IO, dis: Discretization, binary: bool = True, out: bool = True
) -> None:
    if binary:
        io.ens_write_string(fstream, "C Binary", binary=True)

    io.ens_write_string(fstream, "BEGIN TIME STEP", binary=binary)
    io.ens_write_string(fstream, "geometry", binary=binary)
    io.ens_write_string(fstream, "Comment", binary=binary)
    io.ens_write_string(fstream, "node id given", binary=binary)
    io.ens_write_string(fstream, "element id off", binary=binary)  # should I switch on?
    io.ens_write_string(fstream, "part", binary=binary)
    io.ens_write_int(fstream, 1, binary=binary)
    io.ens_write_string(fstream, "field", binary=binary)
    io.ens_write_string(fstream, "coordinates", binary=binary)
    io.ens_write_int(fstream, len(dis.nodes), binary=binary)
    io.ens_write_ints(fstream, np.array([n.id for n in dis.nodes]), binary=binary)
    io.ens_write_floats(fstream, dis.get_node_coords(), binary=binary)

    # build eletype array
    elegroups = {}
    for eles in progress(
        dis.elements.values(), out=out, label="Prepare element geometry"
    ):
        for ele in eles:
            if ele.shape not in shape_to_eletype:
                raise NotImplementedError(
                    "This kind of element is not known: {0}".format(ele.shape)
                )
            eletype = shape_to_eletype[ele.shape]

            if eletype not in elegroups:
                # np.zeros((0,len(ele.nodes)), dtype=int)
                elegroups[eletype] = []

            elegroups[eletype].append(np.array([n.id for n in ele.nodes]))

    for eletype, eles in elegroups.items():
        io.ens_write_string(fstream, eletype, binary=binary)
        io.ens_write_int(fstream, len(eles), binary=binary)
        io.ens_write_ints(fstream, np.array(eles, dtype=int), binary=binary)

    io.ens_write_string(fstream, "END TIME STEP", binary=binary)


def write_element_variable(
    fstream: IO,
    dis: Discretization,
    varname: str,
    data: Dict[str, np.ndarray],
    binary: bool = True,
) -> Tuple[int, int]:
    if binary:
        io.ens_write_string(fstream, "C Binary", binary=True)

    dim = None
    ts = None

    for key, edata in data.items():
        if len(edata.shape) > 3:
            raise RuntimeError("This kind of data is not supported. To many dimensions")

        if len(edata.shape) == 3:
            # This will be interpreted as transient vector data
            data[key] = np.transpose(edata, (1, 0, 2))

        if len(edata.shape) == 2:
            # This will be interpreted as non transient vector data
            data[key] = edata.reshape(tuple([1] + list(edata.shape)))

        if len(edata.shape) == 1:
            # This will be interpreted as non transient scalar data
            data[key] = edata.reshape(tuple([1] + list(edata.shape) + [1]))

        # safety check
        if dim is None:
            dim = data[key].shape[2]
            ts = data[key].shape[0]
        elif dim != data[key].shape[2]:
            raise RuntimeError(
                "The elemnt data of variable {0} have not the correct dimesion accross all elements".format(
                    varname
                )
            )
        elif ts != data[key].shape[0]:
            raise RuntimeError(
                "The elemnt data of variable {0} have not the correct num_timesteps accross all elements".format(
                    varname
                )
            )

    if ts is None:
        raise RuntimeError("Timestep is None")
    if dim is None:
        raise RuntimeError("dim is None")

    for t in range(ts):
        io.ens_write_string(fstream, "BEGIN TIME STEP", binary=binary)
        io.ens_write_string(fstream, "description", binary=binary)
        io.ens_write_string(fstream, "part", binary=binary)
        io.ens_write_int(fstream, 1, binary=binary)

        for k, d in data.items():
            io.ens_write_string(fstream, k, binary=binary)
            io.ens_write_floats(fstream, d[t], binary=binary)

        io.ens_write_string(fstream, "END TIME STEP", binary=binary)

    return ts, dim


def write_node_variable(
    fstream: IO,
    dis: Discretization,
    varname: str,
    data: np.ndarray,
    binary: bool = True,
) -> Tuple[int, int]:
    if binary:
        io.ens_write_string(fstream, "C Binary", binary=True)

    if len(data.shape) > 3:
        raise RuntimeError("This kind of data is not supported. To many dimensions")

    if len(data.shape) == 3:
        # This will be interpreted as transient vector data
        data = np.transpose(data, (1, 0, 2))

    if len(data.shape) == 2:
        # This will be interpreted as non transient vector data
        data = data.reshape(tuple([1] + list(data.shape)))

    if len(data.shape) == 1:
        # This will be interpreted as non transient scalar data
        data = data.reshape(tuple([1] + list(data.shape) + [1]))

    # safety check
    if data.shape[1] != len(dis.nodes):
        raise RuntimeError(
            "The nodal data of variable {0} does not fit".format(varname)
        )

    for tdata in data:
        io.ens_write_string(fstream, "BEGIN TIME STEP", binary=binary)
        io.ens_write_string(fstream, "description", binary=binary)
        io.ens_write_string(fstream, "part", binary=binary)
        io.ens_write_int(fstream, 1, binary=binary)
        io.ens_write_string(fstream, "coordinates", binary=binary)
        io.ens_write_floats(fstream, tdata, binary=binary)
        io.ens_write_string(fstream, "END TIME STEP", binary=binary)

    return data.shape[0], data.shape[2]
