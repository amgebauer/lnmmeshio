# Meshio adapted for use with BACI
![coverage](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/pipeline.svg)
![build](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/coverage.svg)

Based on https://github.com/nschloe/meshio

## Install

You can install the latest version with pip:

```
pip install --extra-index-url=https://lnm-heartgroup.pages.gitlab.lrz.de/packages lnmmeshio
```

## Documentation

Does only read the discretization and currently completely ignores all other sections.

lnmmeshio is currently only tested with STRUCTURE elements

Read/write a mesh into/from the Discretization class
```
import lnmmeshio

# tested formats are Exodus, Gmsh and .dat (only the discretization, all other sections are discarded)
dis = lnmmeshio.read_discr('pathtofile.ext')

# do what ever you want with dis (like add options to the elements or sth like that)

# iterate over all structural elements
for ele in dis.elements.structure:
    # do sth with the element
    pass

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

# write discretization into an arbitrary format
# the only format that is tested is .dat
lnmmeshio.write_discr('pathtofile.ext', dis)
```


See https://github.com/nschloe/meshio

# Make changes and upgrade

* Make your changes and test changes.
* Adapt version number in `VERSION`
* Create a feature branch (best reference it with corresponding issue)
* Create a merge request from feature branch
* Push changes to Gitlab and wait for the pipeline to pass
* Once the MR is merged, the new version is available in the package repository
