from .discretization import Discretization, Element, Node
from .head import Head
from .matbcs import MatBCs
from collections import OrderedDict

class Dat:

    def __init__(self):
        self.head: Head = None
        self.discretization: Discretization = None
        self.matbcs: MatBCs = None
    
    def write(self, dest):
    
        if self.discretization is not None:
            # compute element and node ids
            self.discretization.compute_ids()

        # write header
        if self.head is not None:
            self.head.write(dest)

        # write matbcs
        if self.matbcs is not None:
            self.matbcs.write(dest)

        # write discretization
        if self.discretization is not None:
            self.discretization.write(dest)
