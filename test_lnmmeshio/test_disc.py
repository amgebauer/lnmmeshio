import io
import os
import unittest

import lnmmeshio
import numpy as np
from lnmmeshio import ioutils
from lnmmeshio.nodeset import LineNodeset, PointNodeset, SurfaceNodeset, VolumeNodeset

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestDiscretizationIO(unittest.TestCase):
    def setUp(self):
        pass

    def test_read(self):
        # read dat file
        mesh = lnmmeshio.read_mesh(os.path.join(script_dir, "data", "dummy.dat"))

        # check, whether all nodes are read correctly
        self.assertEqual(mesh.points.shape, (224, 3))

        # check, whether all tet elements were read correctly
        self.assertEqual(mesh.get_cells_type("tetra").shape, (12, 4))
        self.assertEqual(mesh.get_cells_type("tetra10").shape, (12, 10))
        self.assertEqual(mesh.cell_data["material"][0][0], 1)
        self.assertEqual(mesh.cell_data["material"][1][0], 4)
        self.assertEqual(mesh.cell_data["material"][2][0], 5)
        self.assertEqual(mesh.cell_data["material"][3][0], 6)

        # check, whether all hex elements were read correctly
        self.assertEqual(mesh.get_cells_type("hexahedron").shape, (65, 8))

    def test_write(self):
        # read dat file
        mesh = lnmmeshio.read(os.path.join(script_dir, "data", "dummy.dat"), out=True)

        if not os.path.isdir(os.path.join(script_dir, "tmp")):
            os.makedirs(os.path.join(script_dir, "tmp"))

        # write same dat file
        lnmmeshio.write(os.path.join(script_dir, "tmp", "gen.dat"), mesh)

        # check, whether both files are identical
        # self.assertTrue(filecmp.cmp(os.path.join(script_dir, 'data', 'dummy.dat'),
        #    os.path.join((script_dir), 'tmp', 'gen.dat')))

        # check, whether both sections do coincide
        with open(os.path.join(script_dir, "data", "dummy.dat"), "r") as f:
            sections1 = ioutils.read_dat_sections(f)
        with open(os.path.join(script_dir, "tmp", "gen.dat"), "r") as f:
            sections2 = ioutils.read_dat_sections(f)

        self.assertListEqual(
            sorted(list(sections1.keys())), sorted(list(sections2.keys()))
        )

        for key in sections1.keys():
            self.assertListEqual(sorted(sections1[key]), sorted(sections2[key]))

    def test_read_new(self):
        # read discretization
        disc = lnmmeshio.read(os.path.join(script_dir, "data", "dummy.dat"), out=True)

        disc.compute_ids(zero_based=False)

        self.assertEqual(len(disc.nodes), 224)
        self.assertEqual(len(disc.elements.structure), 89)

        self.assertListEqual([ns.id for ns in disc.nodes[0].surfacenodesets], [1, 13])
        self.assertListEqual([ns.id for ns in disc.nodes[47].surfacenodesets], [9])
        self.assertListEqual([ns.id for ns in disc.nodes[147].surfacenodesets], [6])

    def test_write_new(self):
        # build dummy discretization
        d: lnmmeshio.Discretization = lnmmeshio.Discretization()
        d.nodes = [
            lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([0.0, 1.0, 0.0])),
            lnmmeshio.Node(np.array([0.0, 0.0, 1.0])),
        ]
        for i in range(0, 4):
            d.nodes[i].fibers[lnmmeshio.Fiber.TypeFiber1] = lnmmeshio.Fiber(
                np.array([1.0, 0.0, 0.0])
            )
            d.nodes[i].fibers[lnmmeshio.Fiber.TypeFiber2] = lnmmeshio.Fiber(
                np.array([0.0, 1.0, 0.0])
            )

        d.pointnodesets.append(PointNodeset(1))
        d.linenodesets.append(LineNodeset(1))
        d.surfacenodesets.append(SurfaceNodeset(1))
        d.volumenodesets.append(VolumeNodeset(1))

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

        d.elements.structure = [lnmmeshio.Element("SOLIDT4SCATRA", "TET4", d.nodes)]
        d.elements.structure[0].options = {
            "MAT": 1,
            "KINEM": "nonlinear",
            "TYPE": "Std",
        }

        dummy_file = io.StringIO()
        d.write(dummy_file)
        dummy_file.seek(0)

        # read dummy file
        d_new = lnmmeshio.read_baci_discr(dummy_file)
        d_new.compute_ids(zero_based=True)

        self.assertEqual(len(d_new.nodes), 4)
        self.assertEqual(len(d_new.elements.structure), 1)

        self.assertAlmostEqual(
            np.linalg.norm(d_new.nodes[0].coords - np.array([0, 0, 0])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(d_new.nodes[1].coords - np.array([1, 0, 0])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(d_new.nodes[2].coords - np.array([0, 1, 0])), 0.0
        )
        self.assertAlmostEqual(
            np.linalg.norm(d_new.nodes[3].coords - np.array([0, 0, 1])), 0.0
        )

        for i in range(0, 4):
            self.assertAlmostEqual(
                np.linalg.norm(
                    d_new.nodes[i].fibers[lnmmeshio.Fiber.TypeFiber1].fiber
                    - np.array([1, 0, 0])
                ),
                0.0,
            )
            self.assertAlmostEqual(
                np.linalg.norm(
                    d_new.nodes[i].fibers[lnmmeshio.Fiber.TypeFiber2].fiber
                    - np.array([0, 1, 0])
                ),
                0.0,
            )

        self.assertListEqual([n.id for n in d_new.pointnodesets], [0])
        self.assertListEqual(
            [sorted([n.id for n in nds]) for nds in d_new.linenodesets], [[0, 1]]
        )
        self.assertListEqual(
            [sorted([n.id for n in nds]) for nds in d_new.surfacenodesets], [[0, 1, 2]]
        )
        self.assertListEqual(
            [sorted([n.id for n in nds]) for nds in d_new.volumenodesets],
            [[0, 1, 2, 3]],
        )

        self.assertEqual(d_new.elements.structure[0].type, "SOLIDT4SCATRA")
        self.assertEqual(d_new.elements.structure[0].shape, "TET4")
        self.assertListEqual(d_new.elements.structure[0].nodes, d_new.nodes)
        self.assertEqual(d_new.elements.structure[0].options["MAT"], "1")
        self.assertEqual(d_new.elements.structure[0].options["KINEM"], "nonlinear")
        self.assertEqual(d_new.elements.structure[0].options["TYPE"], "Std")

    def test_io_utils_text_fill(self):
        # test text_fill
        self.assertEqual(
            lnmmeshio.ioutils.text_fill("TEST", 10, "-", minimum=10, fill_left=True),
            "----------TEST",
        )
        self.assertEqual(
            lnmmeshio.ioutils.text_fill("TEST", 10, "-", minimum=3, fill_left=True),
            "------TEST",
        )
        self.assertEqual(
            lnmmeshio.ioutils.text_fill("TEST2", 12, "-", minimum=3), "TEST2-------"
        )

    def test_io_utils_write_title(self):
        dummy_file = io.StringIO()

        # test write_title
        lnmmeshio.ioutils.write_title(dummy_file, "TITLE")
        self.assertEqual(
            dummy_file.getvalue(),
            "--------------------------------------------------------------------TITLE\n",
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_title(
            dummy_file,
            "THIS IS A VERY LONG TITLE WHICH TAKES MORE SPACE THAN ALLOWED LETS SEE HOW",
        )
        self.assertEqual(
            dummy_file.getvalue(),
            "---THIS IS A VERY LONG TITLE WHICH TAKES MORE SPACE THAN ALLOWED LETS SEE HOW\n",
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_title(dummy_file, "TITLE", newline=False)
        self.assertEqual(
            dummy_file.getvalue(),
            "--------------------------------------------------------------------TITLE",
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_write_option(self):
        dummy_file = io.StringIO()
        # test write_option
        lnmmeshio.ioutils.write_option(dummy_file, "KEY", "VALUE")
        self.assertEqual(
            dummy_file.getvalue(), "KEY                             VALUE\n"
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option(dummy_file, "KEY", "VALUE", comment="COMMENT")
        self.assertEqual(
            dummy_file.getvalue(),
            "KEY                             VALUE                           // COMMENT\n",
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option(dummy_file, "KEY", "VALUE", newline=False)
        self.assertEqual(dummy_file.getvalue(), "KEY                             VALUE")
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_write_option_list(self):
        dummy_file = io.StringIO()
        # test write_option_list
        lnmmeshio.ioutils.write_option_list(
            dummy_file,
            {"KEY0": "VAL0", "KEY1": ["VAL1.1", "VAL1.2"], "KEY2": [2.1, 2.2]},
        )
        self.assertEqual(
            dummy_file.getvalue(), "KEY0 VAL0 KEY1 VAL1.1 VAL1.2 KEY2 2.1 2.2\n"
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option_list(
            dummy_file,
            {"KEY1": ["VAL1.1", "VAL1.2"], "KEY2": [2.1, 2.2]},
            newline=False,
        )
        self.assertEqual(dummy_file.getvalue(), "KEY1 VAL1.1 VAL1.2 KEY2 2.1 2.2")
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_write_comment(self):
        dummy_file = io.StringIO()
        # test write_comment
        lnmmeshio.ioutils.write_comment(dummy_file, "COMMENT")
        self.assertEqual(dummy_file.getvalue(), "// COMMENT\n")
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_comment(dummy_file, "COMMENT", newline=False)
        self.assertEqual(dummy_file.getvalue(), "// COMMENT")
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_read_dat_sections(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_title(dummy_file, "HEAD1")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY1", "VAL1")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY2", "VAL2")
        lnmmeshio.ioutils.write_title(dummy_file, "HEAD2")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY1", "VAL1")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY2", "VAL2")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY3", "VAL3")
        lnmmeshio.ioutils.write_title(dummy_file, "HEAD3")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY1", "VAL1")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY2", "VAL2")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY3", "VAL3")
        lnmmeshio.ioutils.write_option(dummy_file, "KEY4", "VAL4")

        # seek to beginning
        dummy_file.seek(0)
        sections = lnmmeshio.ioutils.read_dat_sections(dummy_file)
        self.assertListEqual(list(sections.keys()), ["", "HEAD1", "HEAD2", "HEAD3"])
        self.assertListEqual(sections[""], [])
        self.assertEqual(len(sections["HEAD1"]), 2)
        self.assertEqual(len(sections["HEAD2"]), 3)
        self.assertEqual(len(sections["HEAD3"]), 4)

    def test_io_utils_read_option_item(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_option_list(
            dummy_file,
            {
                "KEY1": "VAL1",
                "KEY2": ["VAL2.1", "VAL2.2"],
                "KEY3": 3,
                "KEY4": [4.1, 4.2],
            },
        )

        line = dummy_file.getvalue()
        self.assertEqual(lnmmeshio.ioutils.read_option_item(line, "KEY1")[0], "VAL1")
        self.assertListEqual(
            lnmmeshio.ioutils.read_option_items(line, "KEY2", num=2)[0],
            ["VAL2.1", "VAL2.2"],
        )
        self.assertEqual(lnmmeshio.ioutils.read_option_item(line, "KEY3")[0], "3")
        self.assertListEqual(
            lnmmeshio.ioutils.read_option_items(line, "KEY4", num=2)[0], ["4.1", "4.2"]
        )

        self.assertRaises(
            RuntimeError, lambda: lnmmeshio.ioutils.read_option_item(line, "KEY5")
        )

    def test_io_utils_read_next_option(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_option_list(
            dummy_file,
            {
                "KEY1": "VAL1",
                "KEY2": ["VAL2.1", "VAL2.2"],
                "KEY3": 3,
                "KEY4": [4.1, 4.2],
            },
        )

        line = dummy_file.getvalue()

        for i, (key, values) in enumerate(
            lnmmeshio.ioutils.read_key_values(
                line, lambda key: 2 if key == "KEY2" or key == "KEY4" else 1
            )
        ):
            self.assertEqual(key, f"KEY{i+1}")

            if i == 0:
                self.assertEqual(values, ["VAL1"])
            elif i == 1:
                self.assertListEqual(values, ["VAL2.1", "VAL2.2"])
            elif i == 2:
                self.assertListEqual(values, ["3"])
            elif i == 3:
                self.assertListEqual(values, ["4.1", "4.2"])

    def test_dummy_read(self):
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_title(dummy_file, "TITLE", newline=True)
        lnmmeshio.ioutils.write_title(dummy_file, "TITLE", newline=True)
        dummy_file.seek(0)

        with self.assertRaises(ValueError) as _:
            lnmmeshio.ioutils.read_dat_sections(dummy_file)


if __name__ == "__main__":
    unittest.main()
