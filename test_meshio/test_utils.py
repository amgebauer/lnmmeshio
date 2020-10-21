import io
import os
import unittest

import numpy as np

import lnmmeshio

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def test_points_on_same_side_of_plane(self):
        self.assertTrue(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 2.0]),
                include_plane=True,
            )
        )
        self.assertTrue(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 0.0]),
                include_plane=True,
            )
        )
        self.assertTrue(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 0.0]),
                include_plane=True,
            )
        )
        self.assertFalse(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, -2.0]),
                include_plane=True,
            )
        )
        self.assertFalse(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, -1.0]),
                np.array([0.0, 0.0, 2.0]),
                include_plane=True,
            )
        )
        self.assertFalse(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 0.0]),
                include_plane=False,
            )
        )
        self.assertFalse(
            lnmmeshio.utils.points_on_same_side_of_plane(
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 0.0]),
                include_plane=False,
            )
        )
