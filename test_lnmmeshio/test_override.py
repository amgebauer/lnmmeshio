import os
import shutil
import unittest

import lnmmeshio

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestOverride(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(script_dir, "tmp")):
            os.makedirs(os.path.join(script_dir, "tmp"))

        if not os.path.isfile(os.path.join(script_dir, "tmp", "cube.mesh")):
            shutil.copy(
                os.path.join(script_dir, "data", "cube.mesh"),
                os.path.join(script_dir, "tmp", "cube.mesh"),
            )

    def test_override_write(self):
        self.setUp()

        d = lnmmeshio.read(os.path.join(script_dir, "data", "dummy.dat"))

        with self.assertRaises(FileExistsError):
            lnmmeshio.write(
                os.path.join(script_dir, "tmp", "cube.mesh"), d, override=False
            )

        lnmmeshio.write(os.path.join(script_dir, "tmp", "cube.mesh"), d, override=True)

    def test_override_write_mesh(self):
        self.setUp()
        d = lnmmeshio.read_mesh(os.path.join(script_dir, "data", "dummy.mesh"))

        with self.assertRaises(FileExistsError):
            lnmmeshio.write_mesh(
                os.path.join(script_dir, "tmp", "cube.mesh"), d, override=False
            )

        lnmmeshio.write_mesh(
            os.path.join(script_dir, "tmp", "cube.mesh"), d, override=True
        )
