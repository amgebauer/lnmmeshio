import unittest
import lnmmeshio
import lnmmeshio.dat.ioutils
import lnmmeshio.dat.discretization
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

    def test_read_new(self):
        with open(os.path.join(script_dir, 'data', 'dummy.dat'), 'r') as f:
            sections = lnmmeshio.dat.ioutils.read_dat_sections(f)

            # read discretization
            disc = lnmmeshio.dat.discretization.Discretization.read(sections)

            self.assertEqual(len(disc.nodes), 224)
            self.assertEqual(len(disc.elements[lnmmeshio.dat.discretization.Element.FieldTypeStructure]), 89)
            self.assertEqual(len(disc.elements[lnmmeshio.dat.discretization.Element.FieldTypeTransport]), 0)

            self.assertListEqual(disc.nodes[0].dsurf, [1, 13])
            self.assertListEqual(disc.nodes[47].dsurf, [9])
            self.assertListEqual(disc.nodes[147].dsurf, [6])

if __name__ == '__main__':
    unittest.main()