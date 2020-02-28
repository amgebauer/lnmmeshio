import os
import unittest

import numpy as np

import lnmmeshio as mio
from lnmmeshio.conditions.common_condition import CommonCondition
from lnmmeshio.conditions.condition import ConditionsType
from lnmmeshio.conditions.conditionreader import read_conditions
from lnmmeshio.conditions.line_dirich_conditions import LineDirichletConditions
from lnmmeshio.conditions.line_neumann_conditions import LineNeumannConditions
from lnmmeshio.conditions.point_dirich_condition import \
    PointDirichletConditions
from lnmmeshio.conditions.point_neumann_conditions import \
    PointNeumannConditions
from lnmmeshio.conditions.surf_dirich_condition import \
    SurfaceDirichletConditions
from lnmmeshio.conditions.surf_neumann_condition import \
    SurfaceNeumannConditions
from lnmmeshio.conditions.volume_dirich_conditions import \
    VolumeDirichletConditions
from lnmmeshio.conditions.volume_neumann_conditions import \
    VolumeNeumannConditions
from lnmmeshio.nodeset import (LineNodeset, PointNodeset, SurfaceNodeset,
                               VolumeNodeset)

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestConditions(unittest.TestCase):
    def setUp(self):
        pass

    @staticmethod
    def get_dat():
        # build dummy discretization
        dat: mio.Datfile = mio.Datfile()
        d: mio.Discretization = mio.Discretization()
        dat.discretization = d
        d.nodes = [
            mio.Node(np.array([0.0, 0.0, 0.0])),
            mio.Node(np.array([1.0, 0.0, 0.0])),
            mio.Node(np.array([0.0, 1.0, 0.0])),
            mio.Node(np.array([0.0, 0.0, 1.0])),
        ]

        d.pointnodesets.append(PointNodeset(1))
        d.pointnodesets.append(PointNodeset(2))
        d.linenodesets.append(LineNodeset(1))
        d.linenodesets.append(LineNodeset(2))
        d.surfacenodesets.append(SurfaceNodeset(1))
        d.surfacenodesets.append(SurfaceNodeset(2))
        d.volumenodesets.append(VolumeNodeset(1))
        d.volumenodesets.append(VolumeNodeset(2))

        d.pointnodesets[0].add_node(d.nodes[0])

        # dline
        for i in range(0, 2):
            d.linenodesets[0].add_node(d.nodes[i])

        # dsurf
        for i in range(0, 3):
            d.surfacenodesets[0].add_node(d.nodes[i])

        # dvol
        for i in range(0, 4):
            d.volumenodesets[0].add_node(d.nodes[i])

        d.elements.structure = [mio.Element("SOLIDT4SCATRA", "TET4", d.nodes)]
        d.elements.structure[0].options = {
            "MAT": 1,
            "KINEM": "nonlinear",
            "TYPE": "Std",
        }

        d.finalize()
        return dat

    def test_write_common(self):
        for acton in [
            ConditionsType.ActOnType.POINT,
            ConditionsType.ActOnType.LINE,
            ConditionsType.ActOnType.SURFACE,
            ConditionsType.ActOnType.VOLUME,
        ]:
            dat = TestConditions.get_dat()
            dat.compute_ids(True)

            bc = CommonCondition(
                dat.discretization.surfacenodesets[0],
                np.array([True] * 3 + [False] * 2),
                np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
                acton,
            )

            dummy_file = bc.get_line()

            self.assertEqual(
                "E 0 - NUMDOF 5 ONOFF 1 1 1 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0",
                dummy_file,
            )

    def common_conditions(self, clsref, containerref, head, type):
        dat = TestConditions.get_dat()
        dat.compute_ids(True)

        bcs = containerref()
        bc1 = clsref(
            dat.discretization.surfacenodesets[0],
            np.array([True] * 3 + [False] * 2),
            np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            bcs.acton,
        )
        bc2 = clsref(
            dat.discretization.surfacenodesets[1],
            np.array([True] * 2 + [False] * 3),
            np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            bcs.acton,
        )
        bcs.add(bc1)
        bcs.add(bc2)

        bcs.get_sections()

        self.assertDictEqual(
            dict(bcs.get_sections()),
            {
                "DESIGN {0} {1} CONDITIONS".format(head, type): [
                    "D{0} 2".format(head),
                    "E 0 - NUMDOF 5 ONOFF 1 1 1 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0",
                    "E 1 - NUMDOF 5 ONOFF 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0",
                ]
            },
        )

    def test_write_surfdirich_multiple(self):
        self.common_conditions(
            CommonCondition, SurfaceDirichletConditions, "SURF", "DIRICH"
        )

    def test_write_linedirich_multiple(self):
        self.common_conditions(
            CommonCondition, LineDirichletConditions, "LINE", "DIRICH"
        )

    def test_write_voldirich_multiple(self):
        self.common_conditions(
            CommonCondition, VolumeDirichletConditions, "VOL", "DIRICH"
        )

    def test_write_pointdirich_multiple(self):
        self.common_conditions(
            CommonCondition, PointDirichletConditions, "POINT", "DIRICH"
        )

    def test_write_surfneumann_multiple(self):
        self.common_conditions(
            CommonCondition, SurfaceNeumannConditions, "SURF", "NEUMANN"
        )

    def test_write_lineneumann_multiple(self):
        self.common_conditions(
            CommonCondition, LineNeumannConditions, "LINE", "NEUMANN"
        )

    def test_write_volneumann_multiple(self):
        self.common_conditions(
            CommonCondition, VolumeNeumannConditions, "VOL", "NEUMANN"
        )

    def test_write_pointneumann_multiple(self):
        self.common_conditions(
            CommonCondition, PointNeumannConditions, "POINT", "NEUMANN"
        )

    def test_read_common(self):
        dat = TestConditions.get_dat()

        bc = CommonCondition.read(
            "E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0",
            dat,
            mio.conditions.condition.ConditionsType.ActOnType.SURFACE,
        )

        self.assertEqual(bc.nodeset, dat.discretization.surfacenodesets[0])
        self.assertListEqual(list(bc.onoff), [True] * 3 + [False] * 3)
        self.assertListEqual(list(bc.value), [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

    def read_common_multiple(self, shortname, type):
        dat = TestConditions.get_dat()

        sections = {}
        sections["DESIGN {0} {1} CONDITIONS".format(shortname, type)] = []
        sections["DESIGN {0} {1} CONDITIONS".format(shortname, type)].append(
            "D{0} 2".format(shortname)
        )
        sections["DESIGN {0} {1} CONDITIONS".format(shortname, type)].append(
            "E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0"
        )
        sections["DESIGN {0} {1} CONDITIONS".format(shortname, type)].append(
            "E 2 - NUMDOF 3 ONOFF 1 1 1 VAL 0.1 0.2 0.3 FUNCT 0 0 0"
        )

        bcs = read_conditions(sections, dat)

        self.assertEqual(len(bcs), 1)
        self.assertEqual(len(bcs[0]), 2)
        self.assertListEqual(list(bcs[0][0].onoff), [True] * 3 + [False] * 3)
        self.assertListEqual(list(bcs[0][1].onoff), [True] * 3)
        self.assertListEqual(list(bcs[0][0].value), [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.assertListEqual(list(bcs[0][1].value), [0.1, 0.2, 0.3])

    def test_unknown_condition(self):
        dat = TestConditions.get_dat()

        sections = {}
        sections["DESIGN NONEXISTANT CONDITIONS"] = []
        sections["DESIGN NONEXISTANT CONDITIONS"].append(" //D1 2")
        sections["DESIGN NONEXISTANT CONDITIONS"].append(
            " //E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0"
        )
        self.assertListEqual(read_conditions(sections, dat), [])

        sections["DESIGN NONEXISTANT CONDITIONS"].append("D1 2")
        sections["DESIGN NONEXISTANT CONDITIONS"].append(
            "E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0"
        )

        with self.assertRaises(NotImplementedError):
            read_conditions(sections, dat)

    def test_read_surfdirich_multiple(self):
        self.read_common_multiple("SURF", "DIRICH")

    def test_read_linedirich_multiple(self):
        self.read_common_multiple("LINE", "DIRICH")

    def test_read_voldirich_multiple(self):
        self.read_common_multiple("VOL", "DIRICH")

    def test_read_pointdirich_multiple(self):
        self.read_common_multiple("POINT", "DIRICH")

    def test_read_surfneumann_multiple(self):
        self.read_common_multiple("SURF", "NEUMANN")

    def test_read_lineneumann_multiple(self):
        self.read_common_multiple("LINE", "NEUMANN")

    def test_read_volneumann_multiple(self):
        self.read_common_multiple("VOL", "NEUMANN")

    def test_read_pointneumann_multiple(self):
        self.read_common_multiple("POINT", "NEUMANN")
