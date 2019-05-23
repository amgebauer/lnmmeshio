import unittest
import lnmmeshio
import os
import meshio

script_dir = os.path.dirname(os.path.realpath(__file__))

class TestMeshio2Discretization(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_read_mesh(self):
        # read mesh

        dis: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.mesh'))

        lnmmeshio.write(os.path.join(script_dir, 'tmp', 'dummy_mesh.dat'), dis, file_format='dis')