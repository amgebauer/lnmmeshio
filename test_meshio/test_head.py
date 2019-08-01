import unittest
import lnmmeshio
import os
import filecmp
import io
import numpy as np
import shutil
import filecmp
import meshio
from lnmmeshio.head import Head, CommentLine, MultipleOptionsLine, SingleOptionLine, MultipleOptionsSection, SingleOptionSection, TextSection
from lnmmeshio.datfile import Datfile
from lnmmeshio import ioutils
from collections import OrderedDict
import re

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestHead(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_read_head(self):
        with open(os.path.join(script_dir, 'data', 'full.dat'), 'r') as f:
            sections = ioutils.read_dat_sections(f)
        
        head: Head = Head.read(sections)

        # check, whether that worked
        str_dyn = head['STRUCTURAL DYNAMIC']
        self.assertIsNotNone(str_dyn)

        self.assertEqual(str_dyn['INT_STRATEGY'].value[0], 'Standard')
        self.assertEqual(str_dyn['DYNAMICTYP'].value[0], 'OneStepTheta')

        title = head['TITLE']
        self.assertEqual(len(title), 1)
        self.assertEqual(title[0], 'This is a fancy title')
    
    def test_write_head(self):
        head: Head = Head()

        title_section = TextSection('TITLE', ['This is a fancy title', 'line2'])
        problemtype = SingleOptionSection('PROBLEM TYP', 'Here all ...')
        problemtype.append(SingleOptionLine('PROBLEMTYP', 'Structure', 'This is a fancy comment'))
        problemtype.append(SingleOptionLine('RANDSEED', '1'))

        materials = MultipleOptionsSection('MATERIALS')
        materials.append(MultipleOptionsLine({'MAT': 1, 'DERE': '2'}, 'fancy comment'))
        materials.append(MultipleOptionsLine({'MAT': 12, 'DERE': '23'}))

        head.append(title_section)
        head.append(problemtype)
        head.append(materials)


        dummy_file = io.StringIO()

        head.write(dummy_file)

        lines = dummy_file.getvalue().split('\n')

        self.assertEqual(lines[0], '--------------------------------------------------------------------TITLE')
        self.assertEqual(lines[1], 'This is a fancy title')
        self.assertEqual(lines[2], 'line2')
        self.assertEqual(lines[3], '--------------------------------------------------------------PROBLEM TYP')
        self.assertEqual(lines[4], '// Here all ...')
        self.assertEqual(lines[5], 'PROBLEMTYP                      Structure // This is a fancy comment')
        self.assertEqual(lines[6], 'RANDSEED                        1')
        self.assertEqual(lines[7], '----------------------------------------------------------------MATERIALS')
        self.assertEqual(lines[8], 'MAT 1 DERE 2 // fancy comment')
        self.assertEqual(lines[9], 'MAT 12 DERE 23')

    def test_write_multiple_options_line(self):
        m = MultipleOptionsLine(OrderedDict({'a': 1, 'b': 2}))
        self.assertListEqual(m.get_lines(), ['a 1 b 2'])

        m = MultipleOptionsLine(OrderedDict({'a': 1, 'b': 2}), 'small comment')
        self.assertListEqual(m.get_lines(), ['a 1 b 2 // small comment'])

        m = MultipleOptionsLine(
            OrderedDict({'a': 1, 'b': 2}),
            'this is a very long comment that must be placed on an extra line before'
        )
        self.assertListEqual(m.get_lines(),
            ['// this is a very long comment that must be placed on an extra line before','a 1 b 2']
        )

    def assertRegexListEqual(self, l1, regex):
        self.assertEqual(len(l1), len(regex))
        for l, r in zip(l1, regex):
            self.assertRegexpMatches(l, r)

    def test_single_option_line(self):
        m = SingleOptionLine('key', 'value')

        self.assertRegexListEqual(m.get_lines(), [re.compile(r'^key\s+value$')])

        m = SingleOptionLine('key', 'value', 'small comment')
        self.assertRegexListEqual(m.get_lines(), [re.compile(r'^key\s+value\s+//\s+small comment$')])

        m = SingleOptionLine(
            'key', 'value',
            'this is a very long comment that must be placed on an extra line before'
        )
        self.assertRegexListEqual(m.get_lines(),
            [re.compile(r'^\s*//\s+this is a very long comment that must be placed on an extra line before$'),
                re.compile(r'^key\s+value$')]
        )
    
    def test_parse_multiple_options_line(self):
        inp = 'a 1 b 2 // comment'
        l = MultipleOptionsLine.parse(inp)

        self.assertIsNotNone(l)
        self.assertDictEqual(l.options, {'a': ['1'], 'b': ['2']})
        self.assertEqual(l.comment, 'comment')
    
    def test_parse_comment_line(self):
        inp = '// comment'
        l = CommentLine.parse(inp)

        self.assertIsNotNone(l)
        self.assertEqual(l.comment, 'comment')

        with self.assertRaises(ValueError):
            CommentLine.parse('a // comment')
        
        self.assertIsNone(CommentLine.parse('').comment)