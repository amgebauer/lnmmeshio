import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List

script_dir = os.path.dirname(os.path.realpath(__file__))

class TestMeshio2Discretization(unittest.TestCase):
     
    def setUp(self):
        pass

    def test_get_nodes(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy2.dat'))
        dis.compute_ids()

        # test scalar
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dnode(1)],
            [1]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dline(1)],
            [1, 2]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dsurf(1)],
            [1, 2, 3]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dvol(1)],
            [1, 2, 3, 4]
        )

        # test list
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dnode([1])],
            [1]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dline([1])],
            [1, 2]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dsurf([1])],
            [1, 2, 3]
        )
        self.assertListEqual(
            [n.id for n in dis.get_nodes_by_dvol([1])],
            [1, 2, 3, 4]
        )
        