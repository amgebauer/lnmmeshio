import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List

script_dir = os.path.dirname(os.path.realpath(__file__))

class TestMeshio2Discretization(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_read_mesh(self):
        # read mesh

        dis: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy.mesh'))


        if not os.path.isdir(os.path.join(script_dir, 'tmp')):
            os.makedirs(os.path.join(script_dir, 'tmp'))
            
        lnmmeshio.write(os.path.join(script_dir, 'tmp', 'dummy_mesh.dat'), dis, file_format='dis')
    
    def test_vice_versa(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(os.path.join(script_dir, 'data', 'dummy2.dat'))

        dis2: lnmmeshio.Discretization = lnmmeshio.meshio_to_discretization.mesh2Discretization(
            lnmmeshio.meshio_to_discretization.discretization2mesh(dis)
        )

        dis.compute_ids(zero_based=True)
        dis2.compute_ids(zero_based=True)

        # compare whether both discretizations are the same
        self.assertEqual(len(dis.nodes), len(dis2.nodes))

        # compare each node
        for node1, node2 in zip(dis.nodes, dis2.nodes):
            self.assertAlmostEqual(
                np.linalg.norm(node1.coords - node2.coords), 0
            )

            self.assertListEqual(
                sorted(node1.dpoint), sorted(node2.dpoint)
            )
            self.assertListEqual(
                sorted(node1.dline), sorted(node2.dline)
            )
            self.assertListEqual(
                sorted(node1.dsurf), sorted(node2.dsurf)
            )
        
        eletype_list1: List[str] = []
        eletype_list2: List[str] = []

        for flieldtype, eles in dis.elements.items():
            if len(eles) > 0:
                eletype_list1.append(flieldtype)

        for flieldtype, eles in dis2.elements.items():
            if len(eles) > 0:
                eletype_list2.append(flieldtype)
        
        self.assertListEqual(sorted(eletype_list1), sorted(eletype_list2))
    
        for eletype in eletype_list1:

            self.assertEqual(len(dis.elements[eletype]), len(dis2.elements[eletype]))

            for ele1, ele2 in zip(dis.elements[eletype], dis2.elements[eletype]):
                
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):

                    self.assertEqual(n1.id, n2.id)
