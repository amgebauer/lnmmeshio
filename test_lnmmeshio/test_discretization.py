import os
import unittest

import lnmmeshio

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestMeshio2Discretization(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_dsurf_elements(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy2.dat")
        )

        surface_elements = dis.get_dsurf_elements(0)

        self.assertEqual(len(surface_elements), 1)
        self.assertIsInstance(surface_elements[0], lnmmeshio.Tri3)
        self.assertListEqual(
            sorted([n.id for n in surface_elements[0].nodes]), [0, 1, 2]
        )

    def test_get_dline_elements(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy2.dat")
        )

        line_elements = dis.get_dline_elements(0)

        self.assertEqual(len(line_elements), 1)
        self.assertIsInstance(line_elements[0], lnmmeshio.Line2)
        self.assertListEqual(sorted([n.id for n in line_elements[0].nodes]), [0, 1])

    def test_get_nodes(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy2.dat")
        )
        dis.compute_ids(zero_based=False)

        # test scalar
        self.assertListEqual([n.id for n in dis.pointnodesets[0]], [1])
        self.assertListEqual(sorted([n.id for n in dis.linenodesets[0]]), [1, 2])
        self.assertListEqual(sorted([n.id for n in dis.surfacenodesets[0]]), [1, 2, 3])
        self.assertListEqual(
            sorted([n.id for n in dis.volumenodesets[0]]), [1, 2, 3, 4]
        )

        # test list
        self.assertListEqual([n.id for n in dis.pointnodesets[0]], [1])
        self.assertListEqual(sorted([n.id for n in dis.linenodesets[0]]), [1, 2])
        self.assertListEqual(sorted([n.id for n in dis.surfacenodesets[0]]), [1, 2, 3])
        self.assertListEqual(
            sorted([n.id for n in dis.volumenodesets[0]]), [1, 2, 3, 4]
        )
