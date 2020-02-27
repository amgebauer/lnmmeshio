import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List
from lnmmeshio import Fiber

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestFibers(unittest.TestCase):
    def setUp(self):
        pass

    def test_fibers_parse(self):
        # parse
        ele_def = "1 TYPE SHAPE 1 2 3 MAT 1 FIBER1 0.1 0.2 0.3 FIBER2 0.2 0.3 0.4 CIR 0.3 0.4 0.5 TAN 0.4 0.5 0.6\n"

        # parse fibers
        fibs = Fiber.parse_fibers(ele_def)

        self.assertEqual(len(fibs), 4)

        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber1].fiber - np.array([0.1, 0.2, 0.3])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber2].fiber - np.array([0.2, 0.3, 0.4])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeCir].fiber - np.array([0.3, 0.4, 0.5])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeTan].fiber - np.array([0.4, 0.5, 0.6])), 0.0
        )

        self.assertEqual(Fiber.get_fiber_type("FIBER1"), Fiber.TypeFiber1)
        self.assertEqual(Fiber.get_fiber_type("FIBER2"), Fiber.TypeFiber2)
        self.assertEqual(Fiber.get_fiber_type("CIR"), Fiber.TypeCir)
        self.assertEqual(Fiber.get_fiber_type("TAN"), Fiber.TypeTan)
