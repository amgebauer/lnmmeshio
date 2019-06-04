import unittest
import lnmmeshio
import os
import filecmp
import io
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestEnsight(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_write_ensight(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy2.dat'))
        dis.compute_ids()

        for elelist in dis.elements.values():
            for ele in elelist:
                ele.data['material'] = np.array(float(' '.join(ele.options['MAT'])))
        
        for n in dis.nodes:
            n.data['id'] = np.array([n.id])

        # write ensight
        lnmmeshio.write(os.path.join(script_dir, 'tmp', 'ensight.case'), dis)