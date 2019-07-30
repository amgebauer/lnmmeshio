import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from collections import OrderedDict
import re
from .element.element import Element
from .element.element_container import ElementContainer
from .node import Node
from .fiber import Fiber
from .progress import progress
from .discretization import Discretization
from .functions.function import Function
from .conditions.condition import ConditionsType
from .conditions.conditionreader import read_conditions

"""
This class holds all information in the datfiles, consisting out of the discretization, conditions
and options.
"""
class Datfile:
    
    def __init__(self):
        self.discretization = Discretization()

        # initialize functions
        self.functions: List[Function] = []

        # initialize conditions
        self.conditions = List[ConditionsType]
    
        """
    Computes the ids of the elements and nodes. 

    Args:
        zero_based: If true, the first node id is 0, otherwise 1
    """
    def compute_ids(self, zero_based: bool):
        
        self.discretization.compute_ids(zero_based)
        
        id: int = 0 if zero_based else 1
        for f in self.functions:
            f.id = id
            id += 1
        
        """
    Resets the computed ids
    """
    def reset(self):
        self.discretization.reset()

        for f in self.functions:
            f.reset()


    """
    Static method that creates the discretizations file from the input lines of a .dat file

    Args:
        sections: Dictionary with header titles as keys and list of lines as value
    
    Retuns:
        Discretization object
    """
    @staticmethod
    def read(sections: Dict[str, List[str]], out: bool = False) -> 'Discretization':
        dat = Datfile()
        
        # read discretization
        dat.discretization = Discretization.read(sections, out=out)

        # read functions
        dat.functions = Function.read_functions(sections)

        # read boundary conditions
        dat.conditions = read_conditions(sections, dat)