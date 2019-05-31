# Meshio adapted for use with BACI
![coverage](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/pipeline.svg)
![build](https://gitlab.lrz.de/lnm-heartgroup/meshio/badges/master/coverage.svg)

Forked from https://github.com/nschloe/meshio

# Documentation

Does only read the discretization and currently completely ignores all other sections.

lnmmeshio is currently only tested with STRUCTURE elements

Read mesh into our Discretization format
```
import lnmmeshio

lnmmeshio.read('pathtofile.ext')
```

Write into any format

```
import lnmmeshio

dis: lnmmeshio.Discretization = lnmmeshio.Discretization()
# create discretization
# ...

lnmmeshio.write('pathtofile.ext', dis)
```


See https://github.com/nschloe/meshio

# Make changes and upgrade

* Make your changes and test changes.
* Adapt version number in `setup.py`
* Push changes to Gitlab and set Tag to version number
* Create release using `python setup.py sdist`
* Copy the newly created .tar.gz file in the PyPI directory


# ToDo

* Add more unit tests. Currently only a small subpart of dat io is tested!