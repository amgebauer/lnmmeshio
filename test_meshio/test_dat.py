import unittest
import lnmmeshio
import os
import filecmp

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_read(self):
        # read dat file
        mesh = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.dat'))

        # check, whether all nodes are read correctly
        self.assertEqual( mesh._points.shape, (224,3))

        # check, whether all tet elements were read correctly
        self.assertEqual(mesh._cells['tetra'].shape, (108, 4))

        # check, whether all hex elements were read correctly
        self.assertEqual(mesh._cells['hexahedron'].shape, (65,8))

    def test_write(self):
        # read dat file
        mesh = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.dat'))

        # write same dat file
        lnmmeshio.write(os.path.join(script_dir, 'tmp', 'gen.dat'), mesh)

        # check, whether both files are identical
        self.assertTrue(filecmp.cmp(os.path.join(script_dir, 'data', 'dummy.dat'),
            os.path.join(script_dir, 'tmp', 'gen.dat')))



if __name__ == '__main__':
    unittest.main()