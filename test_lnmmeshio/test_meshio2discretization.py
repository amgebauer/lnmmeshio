import os
import unittest

import lnmmeshio
import numpy as np

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestMeshio2Discretization(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_mesh(self):
        # read mesh

        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy.mesh")
        )

        if not os.path.isdir(os.path.join(script_dir, "tmp")):
            os.makedirs(os.path.join(script_dir, "tmp"))

        lnmmeshio.write(
            os.path.join(script_dir, "tmp", "dummy_mesh.dat"), dis, file_format="dat"
        )

    def test_vice_versa(self):
        dis: lnmmeshio.Discretization = lnmmeshio.read(
            os.path.join(script_dir, "data", "dummy2.dat")
        )

        mesh = lnmmeshio.meshio_to_discretization.discretization2mesh(dis)
        dis2: lnmmeshio.Discretization = (
            lnmmeshio.meshio_to_discretization.mesh2Discretization(mesh)
        )

        dis.compute_ids(zero_based=True)
        dis2.compute_ids(zero_based=True)

        # compare whether both discretizations are the same
        self.assertEqual(len(dis.nodes), len(dis2.nodes))

        # compare each node
        for node1, node2 in zip(dis.nodes, dis2.nodes):
            self.assertAlmostEqual(np.linalg.norm(node1.coords - node2.coords), 0)

        # compare nodesets
        # self.assertEqual(len(dis.pointnodesets), len(dis2.pointnodesets))
        # self.assertEqual(len(dis.linenodesets), len(dis2.linenodesets))
        # self.assertEqual(len(dis.surfacenodesets), len(dis2.surfacenodesets))

        # for pns1, pns2 in zip(dis.pointnodesets, dis2.pointnodesets):
        #    self.assertListEqual([n.id for n in pns1], [n.id for n in pns2])

        # for lns1, pns2 in zip(dis.linenodesets, dis2.linenodesets):
        #    self.assertListEqual([n.id for n in lns1], [n.id for n in lns1])

        # for sns1, pns2 in zip(dis.surfacenodesets, dis2.surfacenodesets):
        #    self.assertListEqual([n.id for n in sns1], [n.id for n in sns1])

        self.assertEqual(
            dis.elements.get_num_structure(), dis2.elements.get_num_structure()
        )
        self.assertEqual(dis.elements.get_num_fluid(), dis2.elements.get_num_fluid())
        self.assertEqual(dis.elements.get_num_ale(), dis2.elements.get_num_ale())
        self.assertEqual(
            dis.elements.get_num_transport(), dis2.elements.get_num_transport()
        )
        self.assertEqual(dis.elements.get_num_thermo(), dis2.elements.get_num_thermo())

        if dis.elements.get_num_structure() > 0:
            for ele1, ele2 in zip(dis.elements.structure, dis2.elements.structure):
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):
                    self.assertEqual(n1.id, n2.id)

        if dis.elements.get_num_ale() > 0:
            for ele1, ele2 in zip(dis.elements.ale, dis2.elements.ale):
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):
                    self.assertEqual(n1.id, n2.id)

        if dis.elements.get_num_fluid() > 0:
            for ele1, ele2 in zip(dis.elements.fluid, dis2.elements.fluid):
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):
                    self.assertEqual(n1.id, n2.id)

        if dis.elements.get_num_transport() > 0:
            for ele1, ele2 in zip(dis.elements.transport, dis2.elements.transport):
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):
                    self.assertEqual(n1.id, n2.id)

        if dis.elements.get_num_thermo() > 0:
            for ele1, ele2 in zip(dis.elements.thermo, dis2.elements.thermo):
                # check, whether nodes are the same within the element
                self.assertEqual(ele1.shape, ele2.shape)
                self.assertEqual(len(ele1.nodes), len(ele2.nodes))

                for n1, n2 in zip(ele1.nodes, ele2.nodes):
                    self.assertEqual(n1.id, n2.id)

    def test_2D_mesh_element_data(self):
        dis = lnmmeshio.Discretization()

        dis.nodes = [
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
            lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
        ]

        dis.elements.structure = [
            lnmmeshio.Tri3(None, [dis.nodes[0], dis.nodes[1], dis.nodes[2]]),
            lnmmeshio.Tri3(None, [dis.nodes[0], dis.nodes[3], dis.nodes[4]]),
        ]

        dis.elements.structure[0].data["test"] = 1
        dis.elements.structure[1].data["test"] = 2

        mesh = lnmmeshio.meshio_to_discretization.discretization2mesh(dis)

        self.assertListEqual(list(mesh.cell_data["test"][0]), [1, 2])
