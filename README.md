# Meshio for BACI

[![pipeline](https://github.com/amgebauer/lnmmeshio/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/amgebauer/lnmmeshio/actions/workflows/build_and_test.yml)

Relies on meshio: https://github.com/nschloe/meshio

## Install

You can install the latest version with pip:

```
pip install lnmmeshio
```

## Documentation

Does only read the discretization and currently completely ignores all other sections.

Read/write a mesh into/from the Discretization class
```
import lnmmeshio

# tested formats are Exodus, Gmsh and .dat (only the discretization, all other sections are discarded)
dis = lnmmeshio.read('pathtofile.ext')

# do what ever you want with the discretization (like add options to the elements or sth like that)

# iterate over all structural elements
for ele in dis.elements.structure:
    # do sth with the element
    ele.options["KINEM"] = "nonlinear"
    ele.options["MAT"] = 1

# iterate over all nodes
for node in dis.nodes:
    # do sth with the node
    pass

# iterate over all surface elements with id 0
for ele in dis.get_dsurf_elements(0):
    # do sth with this element
    pass

# iterate over all surface nodeset nodes with id 0
for node in dis.surfacenodesets[0]:
    # do sth with the node
    pass

# write discretization into an arbitrary format (.dat, .vtu, ...)
lnmmeshio.write('pathtofile.ext', dis)
```

See also https://github.com/nschloe/meshio

## Make changes and upgrade

* Make your changes and test changes.
* Adapt version number in pyproject.toml
* Create a feature branch (best reference it with corresponding issue)
* Create a merge request from feature branch
* Push changes to Gitlab and wait for the pipeline to pass
* Once the MR is merged, the new version is available in the package repository

## List of Contributors

The following developers contributed to lnmmeshio (in alphabetical order):

 * Sebastian Brandstäter
 * Janina Datz
 * Amadeus Gebauer
 * Maire Henke
