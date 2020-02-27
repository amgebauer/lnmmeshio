import lnmmeshio as mio
import os, unittest, io
import numpy as np
from lnmmeshio.nodeset import LineNodeset, PointNodeset, VolumeNodeset, SurfaceNodeset
from lnmmeshio.functions.component import Component
from lnmmeshio.functions.function import Function
from lnmmeshio.functions.linear_interpolation_variable import (
    LinearInterpolationVariable,
)
from lnmmeshio.functions.variablereader import read_variable

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_linearinterpolationvariable(self):
        inp = "VARIABLE 0 NAME a TYPE linearinterpolation NUMPOINTS 3 TIMES 0.0 1.0 2.0 VALUES 0.1 0.2 0.3"

        var = read_variable(inp)

        self.assertIsNotNone(var)

        self.assertIsInstance(var, LinearInterpolationVariable)
        self.assertListEqual(list(var.times), [0.0, 1.0, 2.0])
        self.assertListEqual(list(var.values), [0.1, 0.2, 0.3])
        self.assertEqual(var.name, "a")

    def test_read_unknownvariable(self):
        inp = "VARIABLE 0 NAME a TYPE nonexistantvariable"

        with self.assertRaises(NotImplementedError):
            read_variable(inp)

    def test_read_multiplecomponentvariable(self):
        inp = "VARIABLE 1 NAME a TYPE nonexistantvariable"

        with self.assertRaises(RuntimeError):
            read_variable(inp)

    def test_write_linearinterpolationvariable(self):
        dummy_file = io.StringIO()

        var = LinearInterpolationVariable(
            "a", np.array([0.0, 0.1, 0.2]), np.array([1.0, 1.1, 1.2])
        )

        var.write(dummy_file)

        self.assertEqual(
            dummy_file.getvalue(),
            "VARIABLE 0 NAME a TYPE linearinterpolation NUMPOINTS 3 TIMES 0.0 0.1 0.2 VALUES 1.0 1.1 1.2\n",
        )

    def test_read_component(self):
        inp = "COMPONENT 0 FUNCTION 1*2*3"

        comp = Component.read_component(inp)

        self.assertIsNotNone(comp)
        self.assertIsInstance(comp, Component)
        self.assertEqual(comp.expression, "1*2*3")

    def test_write_component(self):
        dummy_file = io.StringIO()
        comp = Component("abs(x)", 0)

        comp.write(dummy_file)

        self.assertEqual(dummy_file.getvalue(), "COMPONENT 0 FUNCTION abs(x)\n")

    def test_read_function(self):
        sections = {}

        for i in range(1, 8):
            key = "FUNCT{0}".format(i)
            sections[key] = [
                "COMPONENT 0 FUNCTION a",
                "COMPONENT 1 FUNCTION b",
                "COMPONENT 2 FUNCTION a",
                "VARIABLE 0 NAME a TYPE linearinterpolation NUMPOINTS 3 TIMES 0.1 2.2 3.3 VALUES 0.1 0.1 1.2",
                "VARIABLE 0 NAME b TYPE linearinterpolation NUMPOINTS 3 TIMES 0.1 2.2 3.3 VALUES 0.1 0.1 1.2",
            ]

        # check read
        fcns = Function.read_functions(sections)

        self.assertEqual(len(fcns), 7)

        for fcn in fcns:
            self.assertEqual(len(fcn.components), 3)
            self.assertListEqual(list(fcn.variables.keys()), ["a", "b"])

            for comp, expr in zip(fcn.components, ["a", "b", "a"]):
                self.assertEqual(comp.expression, expr)

            for var, name in zip(fcn.variables.values(), ["a", "b"]):
                self.assertEqual(var.name, name)
                self.assertListEqual(list(var.times), [0.1, 2.2, 3.3])
                self.assertListEqual(list(var.values), [0.1, 0.1, 1.2])

    def test_write_function(self):
        fcn = Function(1)
        fcn.add_component(Component("a*c", 0))
        fcn.add_variable(
            LinearInterpolationVariable("a", np.array([0.0, 1.0]), np.array([0.0, 1.0]))
        )

        dummy_file = io.StringIO()

        fcn.write(dummy_file)

        lines = dummy_file.getvalue().split("\n")

        lines[0] = lines[0].strip(" -")
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "FUNCT1")
        self.assertEqual(lines[1], "COMPONENT 0 FUNCTION a*c")
        self.assertEqual(
            lines[2],
            "VARIABLE 0 NAME a TYPE linearinterpolation NUMPOINTS 2 TIMES 0.0 1.0 VALUES 0.0 1.0",
        )
        self.assertEqual(lines[3], "")
