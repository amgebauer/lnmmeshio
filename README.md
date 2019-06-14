# Meshio adapted for use with BACI
![coverage](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/pipeline.svg)
![build](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/coverage.svg)

Forked from https://github.com/nschloe/meshio

# Documentation

Does only read the discretization and currently completely ignores all other sections.

lnmmeshio is currently only tested with STRUCTURE elements

Read/write a mesh into/from the Discretization class
```
import lnmmeshio

# tested formats are Gmsh and .dat (only the discretization, all other sections are discarded)
dis = lnmmeshio.read('pathtofile.ext')

# do what ever you want with dis (like add options to the elements or sth like that)

# write discretization into an arbitrary format
# the only format that is tested is .dat
lnmmeshio.write('pathtofile.ext', dis)
```


See https://github.com/nschloe/meshio

# Make changes and upgrade

* Make your changes and test changes.
* Adapt version number in `setup.py`
* Create a feature branch (best reference it with corresponding issue)
* Create a merge request from feature branch
* Push changes to Gitlab and wait for the pipeline to pass
* ask the merge into master
* Create release using `python setup.py sdist`
* Copy the newly created .tar.gz file in the PyPI directory

# ToDo

* Add more unit tests. Currently only a small subpart of dat io is tested!