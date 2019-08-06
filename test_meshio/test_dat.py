import unittest
import lnmmeshio
import os
import filecmp
import io
import numpy as np
from lnmmeshio.nodeset import PointNodeset, LineNodeset, SurfaceNodeset, VolumeNodeset
from collections import OrderedDict
from lnmmeshio.datfile import Datfile
from lnmmeshio.head import Head, Section
from lnmmeshio.conditions.surf_dirich_condition import SurfaceDirichletConditions
from lnmmeshio.result_description import StructureResultDescription
from lnmmeshio.discretization import Discretization
from lnmmeshio.node import Node
from lnmmeshio.element.tri3 import Tri3
import copy
from lnmmeshio.head import TextSection
from lnmmeshio.functions.function import Function

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestDat(unittest.TestCase):

    @staticmethod
    def get_generic():
        dat = Datfile()

        dat.discretization = Discretization()
        dat.discretization.nodes = [Node([1.0, 0.0, 0.0]), Node([1.0, 1.0, 0.0]), Node([0.0, 0.0, 0.0])]
        dat.discretization.elements.structure = [
            Tri3('TRI3', copy.copy(dat.discretization.nodes))
        ]

        dat.functions = [Function(1)]

        dat.head.append(TextSection('TEST', ['line']))

        dat.conditions = [SurfaceDirichletConditions()]

        dat.result_description.append(StructureResultDescription(dat.discretization.nodes[0], 'dispx', 1e-1, 1e-10))
        return dat

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

    def test_compute_ids(self):

        dat = TestDat.get_generic()

        for zero_based in [True, False]:
            add = 1-int(zero_based)
            dat.compute_ids(zero_based=zero_based)

            self.assertEqual(dat.discretization.nodes[0].id, 0+add)
            self.assertEqual(dat.discretization.nodes[1].id, 1+add)
            self.assertEqual(dat.discretization.nodes[2].id, 2+add)
            self.assertEqual(dat.discretization.elements.structure[0].id, 0+add)
            self.assertEqual(dat.functions[0].id, 0+add)

        dat.reset()
    
        self.assertEqual(dat.discretization.nodes[0].id, None)
        self.assertEqual(dat.discretization.nodes[1].id, None)
        self.assertEqual(dat.discretization.nodes[2].id, None)
        self.assertEqual(dat.discretization.elements.structure[0].id, None)
        self.assertEqual(dat.functions[0].id, None)
        
    def test_write(self):

        dat = TestDat.get_generic()

        sections = dat.get_sections()

        print(sections)
