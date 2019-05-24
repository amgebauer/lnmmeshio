import unittest
import lnmmeshio
import os
import filecmp
import io
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestDat(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_read(self):
        # read dat file
        mesh = lnmmeshio.read_mesh(os.path.join(script_dir, 'data', 'dummy.dat'))

        # check, whether all nodes are read correctly
        self.assertEqual( mesh.points.shape, (224,3))

        # check, whether all tet elements were read correctly
        self.assertEqual(mesh.cells['tetra'].shape, (12, 4))
        self.assertEqual(mesh.cells['tetra10'].shape, (12, 10))
        self.assertEqual(mesh.cell_data['tetra']['medit:ref'][0], 4)
        self.assertEqual(mesh.cell_data['tetra10']['medit:ref'][0], 5)
        self.assertEqual(mesh.cell_data['hexahedron']['medit:ref'][0], 1)

        # check, whether all hex elements were read correctly
        self.assertEqual(mesh.cells['hexahedron'].shape, (65,8))

    def test_write(self):
        # read dat file
        mesh = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.dat'))

        # write same dat file
        lnmmeshio.write(os.path.join(script_dir, 'tmp', 'gen.dat'), mesh)

        # check, whether both files are identical
        self.assertTrue(filecmp.cmp(os.path.join(script_dir, 'data', 'dummy.dat'),
            os.path.join(script_dir, 'tmp', 'gen.dat')))

    def test_read_new(self):
        # read discretization
        disc = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.dat'))

        self.assertEqual(len(disc.nodes), 224)
        self.assertEqual(len(disc.elements[lnmmeshio.Element.FieldTypeStructure]), 89)
        self.assertEqual(len(disc.elements[lnmmeshio.Element.FieldTypeTransport]), 0)

        self.assertListEqual(disc.nodes[0].dsurf, [1, 13])
        self.assertListEqual(disc.nodes[47].dsurf, [9])
        self.assertListEqual(disc.nodes[147].dsurf, [6])

    def test_write_new(self):
        
        # build dummy discretization
        d: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.dat'))
        d.nodes = [
            lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([0.0, 1.0, 0.0])),
            lnmmeshio.Node(np.array([0.0, 0.0, 1.0]))
        ]
        for i in range(0, 4):
            d.nodes[i].fiber1 = np.array([1.0, 0.0, 0.0])
            d.nodes[i].fiber2 = np.array([0.0, 1.0, 0.0])
        
        d.nodes[0].dpoint = [1]

        # dline
        for i in range(0, 2):
            d.nodes[i].dline = [1]

        # dsurf
        for i in range(0, 3):
            d.nodes[i].dsurf = [1]

        # dvol
        for i in range(0, 4):
            d.nodes[i].dvol = [1]

        d.elements[lnmmeshio.Element.FieldTypeStructure] = [
            lnmmeshio.Element('SOLIDT4SCATRA', 'TET4', d.nodes)
        ]
        d.elements[lnmmeshio.Element.FieldTypeStructure][0].options = {
            'MAT': 1, 'KINEM': 'nonlinear', 'TYPE': 'Std'
        }

        dummy_file = io.StringIO()
        d.write(dummy_file)
        dummy_file.seek(0)

        # read dummy file
        d_new = lnmmeshio.read_baci(dummy_file)

        self.assertEqual(len(d_new.nodes), 4)
        self.assertEqual(len(d_new.elements[lnmmeshio.Element.FieldTypeStructure]), 1)

        self.assertAlmostEqual(np.linalg.norm(d_new.nodes[0].coords-np.array([0, 0, 0])), 0.0)
        self.assertAlmostEqual(np.linalg.norm(d_new.nodes[1].coords-np.array([1, 0, 0])), 0.0)
        self.assertAlmostEqual(np.linalg.norm(d_new.nodes[2].coords-np.array([0, 1, 0])), 0.0)
        self.assertAlmostEqual(np.linalg.norm(d_new.nodes[3].coords-np.array([0, 0, 1])), 0.0)

        for i in range(0,4):
            self.assertAlmostEqual(np.linalg.norm(d_new.nodes[i].fiber1-np.array([1, 0, 0])), 0.0)
            self.assertAlmostEqual(np.linalg.norm(d_new.nodes[i].fiber2-np.array([0, 1, 0])), 0.0)
        
        self.assertListEqual(d_new.nodes[0].dpoint, [1])
        self.assertListEqual(d_new.nodes[1].dpoint, [])
        self.assertListEqual(d_new.nodes[2].dpoint, [])
        self.assertListEqual(d_new.nodes[3].dpoint, [])

        self.assertListEqual(d_new.nodes[0].dline, [1])
        self.assertListEqual(d_new.nodes[1].dline, [1])
        self.assertListEqual(d_new.nodes[2].dline, [])
        self.assertListEqual(d_new.nodes[3].dline, [])

        self.assertListEqual(d_new.nodes[0].dsurf, [1])
        self.assertListEqual(d_new.nodes[1].dsurf, [1])
        self.assertListEqual(d_new.nodes[2].dsurf, [1])
        self.assertListEqual(d_new.nodes[3].dsurf, [])

        self.assertListEqual(d_new.nodes[0].dvol, [1])
        self.assertListEqual(d_new.nodes[1].dvol, [1])
        self.assertListEqual(d_new.nodes[2].dvol, [1])
        self.assertListEqual(d_new.nodes[3].dvol, [1])

        
        self.assertEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].type,
            'SOLIDT4SCATRA'
        )
        self.assertEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].shape,
            'TET4'
        )
        self.assertListEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].nodes,
            d_new.nodes
        )
        self.assertListEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].options['MAT'],
            ['1']
        )
        self.assertListEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].options['KINEM'],
            ['nonlinear']
        )
        self.assertListEqual(
            d_new.elements[lnmmeshio.Element.FieldTypeStructure][0].options['TYPE'],
            ['Std']
        )

    def test_io_utils_text_fill(self):
        # test text_fill
        self.assertEqual(
            lnmmeshio.ioutils.text_fill('TEST', 10, '-', minimum=10, fill_left=True),
            '----------TEST'
        )
        self.assertEqual(
            lnmmeshio.ioutils.text_fill('TEST', 10, '-', minimum=3, fill_left=True),
            '------TEST'
        )
        self.assertEqual(
            lnmmeshio.ioutils.text_fill('TEST2', 12, '-', minimum=3),
            'TEST2-------'
        )

    def test_io_utils_write_title(self):
        dummy_file = io.StringIO()

        # test write_title
        lnmmeshio.ioutils.write_title(dummy_file, 'TITLE')
        self.assertEqual(
            dummy_file.getvalue(),
            '--------------------------------------------------------------------TITLE\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_title(dummy_file,
            'THIS IS A VERY LONG TITLE WHICH TAKES MORE SPACE THAN ALLOWED LETS SEE HOW')
        self.assertEqual(
            dummy_file.getvalue(),
            '---THIS IS A VERY LONG TITLE WHICH TAKES MORE SPACE THAN ALLOWED LETS SEE HOW\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_title(dummy_file, 'TITLE', newline=False)
        self.assertEqual(
            dummy_file.getvalue(),
            '--------------------------------------------------------------------TITLE'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_write_option(self):
        dummy_file = io.StringIO()
        # test write_option
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY', 'VALUE')
        self.assertEqual(
            dummy_file.getvalue(),
            'KEY                             VALUE\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option(dummy_file, 'KEY', 'VALUE', comment='COMMENT')
        self.assertEqual(
            dummy_file.getvalue(),
            'KEY                             VALUE                           // COMMENT\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option(dummy_file, 'KEY', 'VALUE', newline=False)
        self.assertEqual(
            dummy_file.getvalue(),
            'KEY                             VALUE'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

    def test_io_utils_write_option_list(self):
        dummy_file = io.StringIO()
        # test write_option_list
        lnmmeshio.ioutils.write_option_list(dummy_file, {'KEY0': 'VAL0', 'KEY1': ['VAL1.1', 'VAL1.2'],'KEY2': [2.1, 2.2]})
        self.assertEqual(
            dummy_file.getvalue(),
            'KEY0 VAL0 KEY1 VAL1.1 VAL1.2 KEY2 2.1 2.2\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_option_list(dummy_file, {'KEY1': ['VAL1.1', 'VAL1.2'],'KEY2': [2.1, 2.2]}, newline=False)
        self.assertEqual(
            dummy_file.getvalue(),
            'KEY1 VAL1.1 VAL1.2 KEY2 2.1 2.2'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)
    
    def test_io_utils_write_comment(self):
        dummy_file = io.StringIO()
        # test write_comment
        lnmmeshio.ioutils.write_comment(dummy_file, 'COMMENT')
        self.assertEqual(
            dummy_file.getvalue(),
            '// COMMENT\n'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)

        lnmmeshio.ioutils.write_comment(dummy_file, 'COMMENT', newline=False)
        self.assertEqual(
            dummy_file.getvalue(),
            '// COMMENT'
        )
        dummy_file.truncate(0)
        dummy_file.seek(0)
    
    def test_io_utils_read_dat_sections(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_title(dummy_file, 'HEAD1')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY1', 'VAL1')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY2', 'VAL2')
        lnmmeshio.ioutils.write_title(dummy_file, 'HEAD2')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY1', 'VAL1')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY2', 'VAL2')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY3', 'VAL3')
        lnmmeshio.ioutils.write_title(dummy_file, 'HEAD3')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY1', 'VAL1')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY2', 'VAL2')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY3', 'VAL3')
        lnmmeshio.ioutils.write_option(dummy_file, 'KEY4', 'VAL4')

        # seek to beginning
        dummy_file.seek(0)
        sections = lnmmeshio.ioutils.read_dat_sections(dummy_file)
        self.assertListEqual(list(sections.keys()), ['', 'HEAD1', 'HEAD2', 'HEAD3'])
        self.assertListEqual(sections[''], [])
        self.assertEqual(len(sections['HEAD1']), 2)
        self.assertEqual(len(sections['HEAD2']), 3)
        self.assertEqual(len(sections['HEAD3']), 4)
    
    def test_io_utils_read_option_item(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_option_list(dummy_file, {
            'KEY1': 'VAL1',
            'KEY2': ['VAL2.1', 'VAL2.2'],
            'KEY3': 3,
            'KEY4': [4.1, 4.2]
        })

        line = dummy_file.getvalue()
        self.assertEqual(
            lnmmeshio.ioutils.read_option_item(line, 'KEY1')[0],
            'VAL1'
        )
        self.assertListEqual(
            lnmmeshio.ioutils.read_option_item(line, 'KEY2', num=2)[0],
            ['VAL2.1', 'VAL2.2']
        )
        self.assertEqual(
            lnmmeshio.ioutils.read_option_item(line, 'KEY3')[0],
            '3'
        )
        self.assertListEqual(
            lnmmeshio.ioutils.read_option_item(line, 'KEY4', num=2)[0],
            ['4.1', '4.2']
        )

    def test_io_utils_read_next_option(self):
        # build file
        dummy_file = io.StringIO()
        lnmmeshio.ioutils.write_option_list(dummy_file, {
            'KEY1': 'VAL1',
            'KEY2': ['VAL2.1', 'VAL2.2'],
            'KEY3': 3,
            'KEY4': [4.1, 4.2]
        })

        line = dummy_file.getvalue()

        line, key, value = lnmmeshio.ioutils.read_next_option(line)
        self.assertEqual(key, 'KEY1')
        self.assertListEqual(value, ['VAL1'])

        line, key, value = lnmmeshio.ioutils.read_next_option(line, num=2)
        self.assertEqual(key, 'KEY2')
        self.assertListEqual(value, ['VAL2.1', 'VAL2.2'])

        line, key, value = lnmmeshio.ioutils.read_next_option(line)
        self.assertEqual(key, 'KEY3')
        self.assertListEqual(value, ['3'])

        line, key, value = lnmmeshio.ioutils.read_next_option(line, num=2)
        self.assertEqual(key, 'KEY4')
        self.assertListEqual(value, ['4.1', '4.2'])


if __name__ == '__main__':
    unittest.main()