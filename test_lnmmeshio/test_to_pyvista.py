import os
import unittest
from typing import List

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestPyvista(unittest.TestCase):

    def setUp(self):
        pass

    def test_to_pyvista(self):
        dis = lnmmeshio.read(os.path.join(script_dir, "data", "dummy2.dat"))

        # convert to pyvista
        mesh = lnmmeshio.to_pyvista(dis)

        np.testing.assert_equal(mesh.cells, np.array([4, 0, 1, 2, 3]))
        np.testing.assert_equal(
            mesh.points,
            np.array(
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
            ),
        )
