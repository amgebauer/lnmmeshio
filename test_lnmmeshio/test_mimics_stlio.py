import filecmp
import os
import shutil
import unittest

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestMimicsStlIO(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(script_dir, "tmp")):
            os.makedirs(os.path.join(script_dir, "tmp"))

    def test_read_mimics_stl(self):
        mesh = lnmmeshio.read_mesh(
            os.path.join(script_dir, "data", "dummy.stl"), file_format="mimicsstl"
        )

        # check, whether everything is ok
        self.assertEqual(len(mesh.cells), 1)
        self.assertEqual(mesh.cells[0].type, "triangle")
        self.assertEqual(mesh.cells[0].data.shape, (18562, 3))
        self.assertEqual(mesh.points.shape, (9283, 3))

        # check, whether material is recognized
        self.assertEqual(np.sum(mesh.cell_data["medit:ref"][0] == 1), 10850)
        self.assertEqual(np.sum(mesh.cell_data["medit:ref"][0] == 2), 2006)
        self.assertEqual(np.sum(mesh.cell_data["medit:ref"][0] == 3), 5706)

    def test_write_mimics_stl(self):
        points = np.array(
            [
                [0, 0, 0],
                [10, 0, 0],
                [10, 10, 0],
                [0, 10, 0],
                [0, 0, 10],
                [10, 0, 10],
                [10, 10, 10],
                [0, 10, 10],
            ],
            dtype=float,
        )

        cells = []
        cells.append(
            (
                "triangle",
                np.array(
                    [
                        [0, 1, 4],
                        [1, 5, 4],
                        [1, 2, 5],
                        [2, 6, 5],
                        [2, 3, 6],
                        [3, 7, 6],
                        [3, 0, 4],
                        [3, 4, 7],
                        [1, 0, 3],
                        [2, 1, 3],
                        [7, 4, 5],
                        [5, 6, 7],
                    ]
                ),
            )
        )
        cell_data = {"medit:ref": np.array([[1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]])}

        mesh = lnmmeshio.Mesh(points, cells, cell_data=cell_data)

        lnmmeshio.write_mesh(
            os.path.join(script_dir, "tmp", "dummy.mesh"),
            mesh,
            file_format="gmsh",
        )
        lnmmeshio.write_mesh(
            os.path.join(script_dir, "tmp", "dummy.stl"),
            mesh,
            file_format="mimicsstl",
        )

        # self.assertTrue(
        #    filecmp.cmp(
        #        os.path.join(script_dir, "data", "cube.mesh"),
        #        os.path.join(script_dir, "tmp", "dummy.mesh"),
        #    )
        # )
        self.assertTrue(
            filecmp.cmp(
                os.path.join(script_dir, "data", "cube.stl"),
                os.path.join(script_dir, "tmp", "dummy.stl"),
            )
        )

    def tearDown(self):
        # delete tmp folder
        # shutil.rmtree(os.path.join(script_dir, "tmp"))
        pass
