import os
import unittest

from lnmmeshio import ElementContainer

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestEleContainer(unittest.TestCase):
    def setUp(self):
        pass

    def test_elecontainer(self):
        c = ElementContainer()

        self.assertFalse(ElementContainer.TypeStructure in c)
        self.assertFalse(ElementContainer.TypeFluid in c)
        self.assertFalse(ElementContainer.TypeALE in c)
        self.assertFalse(ElementContainer.TypeTransport in c)
        self.assertFalse(ElementContainer.TypeThermo in c)

        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeStructure])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeFluid])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeALE])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeTransport])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeThermo])
        self.assertRaises(KeyError, lambda: c["doesnotexist"])
        with self.assertRaises(KeyError) as _:
            c["doesnotexist"] = 1

        c[ElementContainer.TypeStructure] = [1]
        self.assertListEqual(c[ElementContainer.TypeStructure], [1])
        self.assertListEqual(c.structure, [1])

        c[ElementContainer.TypeFluid] = [2]
        self.assertListEqual(c[ElementContainer.TypeFluid], [2])
        self.assertListEqual(c.fluid, [2])

        c[ElementContainer.TypeALE] = [3]
        self.assertListEqual(c[ElementContainer.TypeALE], [3])
        self.assertListEqual(c.ale, [3])

        c[ElementContainer.TypeTransport] = [4]
        self.assertListEqual(c[ElementContainer.TypeTransport], [4])
        self.assertListEqual(c.transport, [4])

        c[ElementContainer.TypeThermo] = [5]
        self.assertListEqual(c[ElementContainer.TypeThermo], [5])
        self.assertListEqual(c.thermo, [5])

        self.assertTrue(ElementContainer.TypeStructure in c)
        self.assertTrue(ElementContainer.TypeFluid in c)
        self.assertTrue(ElementContainer.TypeALE in c)
        self.assertTrue(ElementContainer.TypeTransport in c)
        self.assertTrue(ElementContainer.TypeThermo in c)
