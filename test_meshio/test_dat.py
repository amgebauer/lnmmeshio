import unittest
import lnmmeshio
import os
import filecmp
import io
import numpy as np
from lnmmeshio.nodeset import PointNodeset, LineNodeset, SurfaceNodeset, VolumeNodeset
from collections import OrderedDict
from lnmmeshio.datfile import Datfile


script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestDat(unittest.TestCase):

    def test_reorder_sections(self):
        sections = OrderedDict()
        sections['END'] = ['1']
        sections['MATERIALS'] = ['2']
        sections['RESULT DESCRIPTION'] = ['3']
        sections['DVOL-NODE TOPOLOGY'] = ['4']
        sections['DESIGN DESCRIPTION'] = ['5']
        sections['STRUCTURAL ELEMENTS'] = ['6']
        sections['NODE COORDS'] = ['7']
        sections['PROBLEM SIZE'] = ['8']
        sections['PROBLEM TYP'] = ['9']
        sections[''] = ['10']
        sections['DESIGN POINT DIRICH CONDITIONS'] = ['11']
        sections['DESIGN SURF DIRICH CONDITIONS'] = ['12']
        sections['OTHER'] = ['13']
        sections['AOTHER'] = ['14']
        sections['FUNCT2'] = ['15']
        sections['FUNCT1'] = ['16']
        sections['TITLE'] = ['17']

        # sort
        sections_sorted = Datfile.reorder_sections(sections)

        # check, whether order is ok
        self.assertListEqual(list(sections_sorted.keys()),
            ['', 'TITLE', 'PROBLEM SIZE', 'PROBLEM TYP', 'AOTHER', 'OTHER', 'MATERIALS',
            'FUNCT1', 'FUNCT2', 'RESULT DESCRIPTION', 'DESIGN POINT DIRICH CONDITIONS',
            'DESIGN SURF DIRICH CONDITIONS', 'DESIGN DESCRIPTION', 'DVOL-NODE TOPOLOGY',
            'NODE COORDS', 'STRUCTURAL ELEMENTS', 'END']
        )

        # check, whether contents hasn't changed
        for k in sections.keys():
            self.assertListEqual(sections[k], sections_sorted[k])
