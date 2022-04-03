import filecmp
import os
import unittest

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestEnsight(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir(os.path.join(script_dir, "tmp")):
            os.makedirs(os.path.join(script_dir, "tmp"))

    def test_write_ensight_ascii(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy.dat")
        )
        dis.compute_ids(zero_based=False)

        for elelist in dis.elements.values():
            for ele in elelist:
                ele.data["material"] = np.array(float(" ".join(ele.options["MAT"])))

        for n in dis.nodes:
            n.data["id"] = np.array([n.id])

        # write ensight
        lnmmeshio.ensightio.write_case(
            os.path.join(script_dir, "tmp", "ensight_ascii.case"),
            dis,
            binary=False,
            override=True,
        )

        # how to check?

    def test_write_ensight_binary(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy.dat")
        )
        dis.compute_ids(zero_based=False)

        for elelist in dis.elements.values():
            for ele in elelist:
                ele.data["material"] = np.array(float(" ".join(ele.options["MAT"])))

        for n in dis.nodes:
            n.data["id"] = np.array([n.id])

        # write ensight
        lnmmeshio.ensightio.write_case(
            os.path.join(script_dir, "tmp", "ensight_binary.case"),
            dis,
            binary=True,
            override=True,
        )

        # how to check?

    def test_write_float(self):
        ref_file = os.path.join(script_dir, "tmp", "ref.tmp")
        res_file = os.path.join(script_dir, "tmp", "res.tmp")

        arr = np.random.rand(10, 20)

        # write ref binary file
        with open(ref_file, "wb") as f:
            np.ravel(arr, "F").astype("<f").tofile(f)

        # test binary
        with open(res_file, "wb") as f:
            lnmmeshio.ioutils.ens_write_floats(f, arr, binary=True)

        self.assertTrue(filecmp.cmp(res_file, ref_file))

        # write ref ascii file
        with open(ref_file, "w") as f:
            for v in np.ravel(arr, "F").astype("<f"):
                if v >= 0:
                    f.write(" ")

                f.write("{0:10.5e}\n".format(v))

        # test binary
        with open(res_file, "w") as f:
            lnmmeshio.ioutils.ens_write_floats(f, arr, binary=False)

        self.assertTrue(filecmp.cmp(res_file, ref_file))

    def test_write_ints(self):
        ref_file = os.path.join(script_dir, "tmp", "ref.tmp")
        res_file = os.path.join(script_dir, "tmp", "res.tmp")

        arr = np.arange(20).reshape((2, -1))

        # write ref binary file
        with open(ref_file, "wb") as f:
            np.ravel(arr).astype("<i").tofile(f)

        # test binary
        with open(res_file, "wb") as f:
            lnmmeshio.ioutils.ens_write_ints(f, arr, binary=True)

        self.assertTrue(filecmp.cmp(res_file, ref_file))

    def tearDown(self):
        pass
        # delete tmp folder
        # shutil.rmtree(os.path.join(script_dir, 'tmp'))
