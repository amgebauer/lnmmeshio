import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List
from lnmmeshio.element.parse_element import parse as parse_ele
from lnmmeshio.node import Node
from lnmmeshio import Hex8
from lnmmeshio import Hex20
from lnmmeshio import Hex27
from lnmmeshio import Tet10
from lnmmeshio import Tet4
from lnmmeshio import Quad4
from lnmmeshio import Quad8
from lnmmeshio import Quad9
from lnmmeshio import Tri3
from lnmmeshio import Tri6
from lnmmeshio import Line2
from lnmmeshio import Line3
from lnmmeshio import Element
from lnmmeshio.nodeset import VolumeNodeset, SurfaceNodeset, LineNodeset, PointNodeset

script_dir = os.path.dirname(os.path.realpath(__file__))

class TestEles(unittest.TestCase):
     
    def setUp(self):
        pass

    def __get_nodes(self, n):
        nodes = [
            Node(np.random.rand(3)) for i in range(n)
        ]

        for i, n in enumerate(nodes):
            n.id = i

        return nodes

    def test_common(self):
        ele = Element(None, 'X', self.__get_nodes(3))

        vnds = [VolumeNodeset(0), VolumeNodeset(1), VolumeNodeset(2), VolumeNodeset(3)]
        snds = [SurfaceNodeset(10), SurfaceNodeset(11), SurfaceNodeset(12), SurfaceNodeset(13)]
        lnds = [LineNodeset(20), LineNodeset(21), LineNodeset(22), LineNodeset(23)]
        pnds = [PointNodeset(30), PointNodeset(31), PointNodeset(32), PointNodeset(33)]

        for i in [0, 1, 2, 3]: vnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]: vnds[i].add_node(ele.nodes[1])
        for i in [0, 1]: vnds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]: snds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]: snds[i].add_node(ele.nodes[1])
        for i in [0, 1]: snds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]: lnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]: lnds[i].add_node(ele.nodes[1])
        for i in [0, 1]: lnds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]: pnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]: pnds[i].add_node(ele.nodes[1])
        for i in [0, 1]: pnds[i].add_node(ele.nodes[2])

        for ns in vnds:
            for n in ns:
                n.volumenodesets.append(ns)
        for ns in snds:
            for n in ns:
                n.surfacenodesets.append(ns)
        for ns in lnds:
            for n in ns:
                n.linenodesets.append(ns)
        for ns in pnds:
            for n in ns:
                n.pointnodesets.append(ns)
            
        self.assertListEqual(sorted([ns.id for ns in ele.get_dvols()]), [0, 1])
        self.assertListEqual(sorted([ns.id for ns in ele.get_dsurfs()]), [10, 11])
        self.assertListEqual(sorted([ns.id for ns in ele.get_dlines()]), [20, 21])
        self.assertListEqual(sorted([ns.id for ns in ele.get_dpoints()]), [30, 31])

    def __test_ele(self, shape, cls, nnodes, faces, facetype, edges, edgetype):

        ele = parse_ele('1 ELENAME {0} {1} MAT 11 KINEM nonlinear TYPE Std'.format(shape, ' '.join([str(i) for i in range(1, nnodes+1)])), self.__get_nodes(nnodes))

        self.assertEqual(int(ele.options['MAT'][0]), 11)

        self.assertIsInstance(ele, cls)

        self.assertEqual(ele.shape, cls.ShapeName)
        self.assertEqual(ele.shape, shape)

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), nnodes)

        f = ele.get_faces()
        self.assertEqual(len(f), len(faces))
        for i, face in enumerate(f):
            self.assertEqual(face.shape, facetype.ShapeName)

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, faces[i][j])

        # test edges
        e = ele.get_edges()
        self.assertEqual(len(e), len(edges))
        for i, edge in enumerate(e):
            self.assertEqual(edge.shape, edgetype.ShapeName)


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, edges[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_hex8(self):
        FACES = [[0, 1, 2, 3], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
        EDGES = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4]]
        
        # test ele
        self.__test_ele('HEX8', Hex8, 8, FACES, Quad4, EDGES, Line2)

    def test_hex20(self):
        FACES = [
            [0, 1, 2, 3, 8, 9, 10, 11],
            [0, 1, 5, 4, 8, 13, 16, 12],
            [1, 2, 6, 5, 9, 14, 17, 13],
            [2, 3, 7, 6, 10, 15, 18, 14],
            [3, 0, 4, 7, 11, 12, 19, 15],
            [4, 5, 6, 7, 15, 17, 18, 19]]
        EDGES = [[0, 1, 8], [1, 2, 9], [2, 3, 10], [3, 0, 11], [0, 4, 12], [1, 5, 13], [2, 6, 14], [3, 7, 15], [4, 5, 16], [5, 6, 17], [6, 7, 18], [7, 4, 19]]

        # test ele
        self.__test_ele('HEX20', Hex20, 20, FACES, Quad8, EDGES, Line3)

    def test_hex27(self):
        FACES = [
            [0, 1, 2, 3, 8, 9, 10, 11, 20],
            [0, 1, 5, 4, 8, 13, 16, 12, 21],
            [1, 2, 6, 5, 9, 14, 17, 13, 22],
            [2, 3, 7, 6, 10, 15, 18, 14, 23],
            [3, 0, 4, 7, 11, 12, 19, 15, 24],
            [4, 5, 6, 7, 15, 17, 18, 19, 25]]
        EDGES = [[0, 1, 8], [1, 2, 9], [2, 3, 10], [3, 0, 11], [0, 4, 12], [1, 5, 13], [2, 6, 14], [3, 7, 15], [4, 5, 16], [5, 6, 17], [6, 7, 18], [7, 4, 19]]
        
        self.__test_ele('HEX27', Hex27, 27, FACES, Quad9, EDGES, Line3)

    def test_tet10(self):
        FACES = [[0, 1, 3, 4, 8, 7], [1, 2, 3, 5, 9, 8], [2, 0, 3, 6, 7, 9], [0, 2, 1, 6, 5, 4]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 0, 6], [0, 3, 7], [1, 3, 8], [2, 3, 9]]
        
        # parse
        self.__test_ele('TET10', Tet10, 10, FACES, Tri6, EDGES, Line3)

    def test_tet4(self):
        FACES = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]
        EDGES = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]]
        
        # parse
        self.__test_ele('TET4', Tet4, 4, FACES, Tri3, EDGES, Line2)

    def test_quad4(self):
        FACES = [[0, 1, 2, 3]]
        EDGES = [[0, 1], [1, 2], [2, 3], [3, 0]]
        
        # parse
        self.__test_ele('QUAD4', Quad4, 4, FACES, Quad4, EDGES, Line2)

    def test_quad8(self):
        FACES = [[0, 1, 2, 3, 4, 5, 6, 7, 8]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 3, 6], [3, 0, 7]]
        
        self.__test_ele('QUAD8', Quad8, 8, FACES, Quad8, EDGES, Line3)

    def test_quad9(self):
        FACES = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 3, 6], [3, 0, 7]]
        
        self.__test_ele('QUAD9', Quad9, 9, FACES, Quad9, EDGES, Line3)

    def test_tri3(self):
        FACES = [[0, 1, 2]]
        EDGES = [[0, 1], [1, 2], [2, 0]]
        
        self.__test_ele('TRI3', Tri3, 3, FACES, Tri3, EDGES, Line2)

    def test_tri6(self):
        FACES = [[0, 1, 2, 3, 4, 5]]
        EDGES = [[0, 1, 3], [1, 2, 4], [2, 0, 5]]
        
        self.__test_ele('TRI6', Tri6, 6, FACES, Tri6, EDGES, Line3)


    def test_line2(self):
        EDGES = [[0, 1]]
    
        self.__test_ele('LINE2', Line2, 2, [], None, EDGES, Line2)

    def test_line3(self):
        EDGES = [[0, 1, 2]]
    
        self.__test_ele('LINE3', Line3, 3, [], None, EDGES, Line3)
