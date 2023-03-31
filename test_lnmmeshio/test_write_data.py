import os
import shutil
import tempfile
import unittest

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestWriteData(unittest.TestCase):
    def test_write_element_data(self):
        d = lnmmeshio.Discretization()
        d.nodes = [
            lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([2.0, 0.0, 0.0])),
        ]
        d.elements.structure = [
            lnmmeshio.Line2("LINE", [d.nodes[0], d.nodes[1]]),
            lnmmeshio.Line2("LINE", [d.nodes[1], d.nodes[2]]),
        ]

        d.elements.structure[1].data["test"] = 1

        with tempfile.TemporaryDirectory() as tmp:
            filename = os.path.join(tmp, "test.vtu")
            lnmmeshio.write(filename, d)

            dis_read = lnmmeshio.read(filename)

            self.assertIsNotNone(dis_read.elements.structure)
            self.assertEqual(len(dis_read.elements.structure), 2)
            self.assertIn("test", dis_read.elements.structure[0].data)
            self.assertIn("test", dis_read.elements.structure[1].data)
            self.assertAlmostEqual(dis_read.elements.structure[0].data["test"], 0)
            self.assertAlmostEqual(dis_read.elements.structure[1].data["test"], 1)

    def test_write_node_data(self):
        d = lnmmeshio.Discretization()
        d.nodes = [
            lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([2.0, 0.0, 0.0])),
        ]
        d.elements.structure = [
            lnmmeshio.Line2("LINE", [d.nodes[0], d.nodes[1]]),
            lnmmeshio.Line2("LINE", [d.nodes[1], d.nodes[2]]),
        ]

        d.nodes[1].data["test"] = 1

        with tempfile.TemporaryDirectory() as tmp:
            filename = os.path.join(tmp, "test.vtu")
            lnmmeshio.write(filename, d)

            dis_read = lnmmeshio.read(filename)

            self.assertEqual(len(dis_read.nodes), 3)

            for i in range(3):
                self.assertIn("test", dis_read.nodes[i].data)
                self.assertAlmostEqual(dis_read.nodes[i].data["test"], int(i == 1))
