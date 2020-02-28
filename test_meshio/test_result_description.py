import copy
import os
import unittest

from lnmmeshio.datfile import Datfile
from lnmmeshio.discretization import Discretization
from lnmmeshio.element.element import Element
from lnmmeshio.element.tri3 import Tri3
from lnmmeshio.functions.function import Function
from lnmmeshio.node import Node
from lnmmeshio.result_description import ResultDescription, StructureResultDescription

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestResultDescription(unittest.TestCase):
    def setUp(self):
        pass

    @staticmethod
    def get_gen_datfile():
        dat = Datfile()

        dat.discretization = Discretization()
        dat.discretization.nodes = [
            Node([1.0, 0.0, 0.0]),
            Node([1.0, 1.0, 0.0]),
            Node([0.0, 0.0, 0.0]),
        ]
        dat.discretization.elements.structure = [
            Tri3("TRI3", copy.copy(dat.discretization.nodes))
        ]

        dat.functions = [Function(1)]
        return dat

    def test_read_description(self):
        d = TestResultDescription.get_gen_datfile()
        d.compute_ids(zero_based=False)

        l1 = "STRUCTURE DIS structure NODE 2 QUANTITY dispz VALUE 8.00901026463622223e+00 TOLERANCE 1e-6"
        l2 = "STRUCTURE DIS structure ELEMENT 1 QUANTITY dispz VALUE 8.00901026463622223e+00 TOLERANCE 1e-6"

        desc1 = ResultDescription.parse(l1, d)
        desc2 = ResultDescription.parse(l2, d)

        self.assertIsInstance(desc1, StructureResultDescription)
        self.assertIsInstance(desc1.item, Node)
        self.assertEqual(desc1.item.id, 2)
        self.assertEqual(desc1.quantity, "dispz")
        self.assertAlmostEqual(desc1.value, 8.00901026463622223e00)
        self.assertAlmostEqual(desc1.tolerance, 1e-6)

        self.assertIsInstance(desc2, StructureResultDescription)
        self.assertIsInstance(desc2.item, Element)
        self.assertEqual(desc2.item.id, 1)
        self.assertEqual(desc2.quantity, "dispz")
        self.assertAlmostEqual(desc2.value, 8.00901026463622223e00)
        self.assertAlmostEqual(desc2.tolerance, 1e-6)

    def test_write_description(self):
        d = TestResultDescription.get_gen_datfile()
        d.compute_ids(zero_based=False)

        desc1 = StructureResultDescription(
            d.discretization.nodes[0], "dispx", 1e-4, 1e-20
        )
        desc2 = StructureResultDescription(
            d.discretization.elements.structure[0], "dispx", 1e-4, 1e-20
        )

        self.assertEqual(
            desc1.get_line(),
            "STRUCTURE DIS structure NODE 1 QUANTITY dispx VALUE 0.0001 TOLERANCE 1e-20",
        )
        self.assertEqual(
            desc2.get_line(),
            "STRUCTURE DIS structure ELEMENT 1 QUANTITY dispx VALUE 0.0001 TOLERANCE 1e-20",
        )

    def test_parse_result_descriptions(self):
        d = TestResultDescription.get_gen_datfile()
        d.compute_ids(zero_based=False)

        sections = {}
        sections["RESULT DESCRIPTION"] = [
            "STRUCTURE DIS structure NODE 2 QUANTITY dispz VALUE 8.00901026463622223e+00 TOLERANCE 1e-6",
            "STRUCTURE DIS structure ELEMENT 1 QUANTITY dispz VALUE 8.00901026463622223e+00 TOLERANCE 1e-6",
        ]

        l = ResultDescription.parseall(sections, d)

        self.assertEqual(len(l), 2)

        self.assertIsInstance(l[0], StructureResultDescription)
        self.assertIsInstance(l[0].item, Node)
        self.assertEqual(l[0].item.id, 2)
        self.assertEqual(l[0].quantity, "dispz")
        self.assertAlmostEqual(l[0].value, 8.00901026463622223e00)
        self.assertAlmostEqual(l[0].tolerance, 1e-6)

        self.assertIsInstance(l[1], StructureResultDescription)
        self.assertIsInstance(l[1].item, Element)
        self.assertEqual(l[1].item.id, 1)
        self.assertEqual(l[1].quantity, "dispz")
        self.assertAlmostEqual(l[1].value, 8.00901026463622223e00)
        self.assertAlmostEqual(l[1].tolerance, 1e-6)
