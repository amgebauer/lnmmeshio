import os
import unittest
from typing import List

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestElementFactory(unittest.TestCase):
    def setUp(self):
        pass

    @staticmethod
    def get_nodes(num: int) -> List[lnmmeshio.Node]:
        return [lnmmeshio.Node(np.array([0, 0, 0])) for i in range(num)]

    def test_element_factory(self):
        self.assert_element(lnmmeshio.Tet10, 10)
        self.assert_element(lnmmeshio.Tet4, 4)
        self.assert_element(lnmmeshio.Hex8, 8)
        self.assert_element(lnmmeshio.Hex20, 20)
        self.assert_element(lnmmeshio.Hex27, 27)

    def assert_element(self, cls, numnodes: int):
        ele = lnmmeshio.element.factory(
            cls.ShapeName, TestElementFactory.get_nodes(numnodes)
        )
        self.assertIsInstance(ele, cls)
