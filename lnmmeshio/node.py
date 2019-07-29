import numpy as np
from typing import Dict, List
from .fiber import Fiber

"""
Class that holds all information of nodes like coords, fibers, nodesets (and additional data)
"""
class Node:

    """
    Initialize node at the coordinades coords

    Args:
        coords: np.array((3)) Coordinates of the node
    """
    def __init__(self, coords: np.array = np.zeros((3))):
        self.id = None
        self.coords: np.array = coords
        self.fibers: Dict[str, Fiber] = {}

        self.pointnodesets = []
        self.linenodesets = []
        self.surfacenodesets = []
        self.volumenodesets = []
        self.data = {}
    
    """
    Sets the id to None
    """
    def reset(self):
        self.id = None
    
    """
    Writes the corresponding line in to the stream variable

    Args:
        dest: stream variable where to write the line
    """
    def write(self, dest):
        if len(self.fibers) > 0:
            dest.write('FNODE')
        else:
            dest.write('NODE')
        
        if self.id is None:
            raise RuntimeError('You have to compute ids before writing')
        
        dest.write(' {0} COORD {1}'.format(self.id, ' '.join([repr(i) for i in self.coords])))
        
        for k, f in self.fibers.items():
            dest.write(' ')
            f.write(dest, k)

        dest.write('\n')