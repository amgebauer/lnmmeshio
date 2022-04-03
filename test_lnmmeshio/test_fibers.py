import os
import unittest

import numpy as np
from lnmmeshio import Fiber

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestFibers(unittest.TestCase):
    def setUp(self):
        pass

    def test_fibers_parse(self):
        # parse
        ele_def = "1 TYPE SHAPE 1 2 3 MAT 1 FIBER1 0.1 0.2 0.3 FIBER2 0.2 0.3 0.4 FIBER3 0.01 0.02 0.03 FIBER4 0.04 0.05 0.06 FIBER5 0.05 0.06 0.07 FIBER6 0.08 0.08 0.1 FIBER7 0.2 0.1 0.01 FIBER8 0.3 0.2 0.2 FIBER9 0.01 0.2 0.9 CIR 0.3 0.4 0.5 TAN 0.4 0.5 0.6 RAD 0.5 0.1 0.1 AXI 0.5 0.6 0.8\n"

        # parse fibers
        fibs = Fiber.parse_fibers(ele_def)

        self.assertEqual(len(fibs), 13)

        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber1].fiber - np.array([0.1, 0.2, 0.3])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber2].fiber - np.array([0.2, 0.3, 0.4])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber3].fiber - np.array([0.01, 0.02, 0.03])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber4].fiber - np.array([0.04, 0.05, 0.06])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber5].fiber - np.array([0.05, 0.06, 0.07])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber6].fiber - np.array([0.08, 0.08, 0.1])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber7].fiber - np.array([0.2, 0.1, 0.01])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber8].fiber - np.array([0.3, 0.2, 0.2])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeFiber9].fiber - np.array([0.01, 0.2, 0.9])),
            0.0,
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeCir].fiber - np.array([0.3, 0.4, 0.5])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeTan].fiber - np.array([0.4, 0.5, 0.6])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeAxi].fiber - np.array([0.5, 0.6, 0.8])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(fibs[Fiber.TypeRad].fiber - np.array([0.5, 0.1, 0.1])), 0.0
        )

        self.assertEqual(Fiber.get_fiber_type("FIBER1"), Fiber.TypeFiber1)
        self.assertEqual(Fiber.get_fiber_type("FIBER2"), Fiber.TypeFiber2)
        self.assertEqual(Fiber.get_fiber_type("FIBER3"), Fiber.TypeFiber3)
        self.assertEqual(Fiber.get_fiber_type("FIBER4"), Fiber.TypeFiber4)
        self.assertEqual(Fiber.get_fiber_type("FIBER5"), Fiber.TypeFiber5)
        self.assertEqual(Fiber.get_fiber_type("FIBER6"), Fiber.TypeFiber6)
        self.assertEqual(Fiber.get_fiber_type("FIBER7"), Fiber.TypeFiber7)
        self.assertEqual(Fiber.get_fiber_type("FIBER8"), Fiber.TypeFiber8)
        self.assertEqual(Fiber.get_fiber_type("FIBER9"), Fiber.TypeFiber9)
        self.assertEqual(Fiber.get_fiber_type("CIR"), Fiber.TypeCir)
        self.assertEqual(Fiber.get_fiber_type("TAN"), Fiber.TypeTan)
        self.assertEqual(Fiber.get_fiber_type("AXI"), Fiber.TypeAxi)
        self.assertEqual(Fiber.get_fiber_type("RAD"), Fiber.TypeRad)
