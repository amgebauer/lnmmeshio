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

        ele.nodes[0].dvol = [0, 1, 2, 3]
        ele.nodes[1].dvol = [0, 1, 2]
        ele.nodes[2].dvol = [0, 1]

        ele.nodes[0].dsurf = [10, 11, 12, 13]
        ele.nodes[1].dsurf = [10, 11, 12]
        ele.nodes[2].dsurf = [10, 11]

        ele.nodes[0].dline = [20, 21, 22, 23]
        ele.nodes[1].dline = [20, 21, 22]
        ele.nodes[2].dline = [20, 21]

        ele.nodes[0].dpoint = [30, 31, 32, 33]
        ele.nodes[1].dpoint = [30, 31, 32]
        ele.nodes[2].dpoint = [30, 31]

        self.assertListEqual(ele.get_dvols(), [0, 1])
        self.assertListEqual(ele.get_dsurfs(), [10, 11])
        self.assertListEqual(ele.get_dlines(), [20, 21])
        self.assertListEqual(ele.get_dpoints(), [30, 31])

    def __test_ele(self, shape, cls, nnodes, faces, facetype, edges, edgetype):

        ele = parse_ele('1 ELENAME {0} {1} MAT 1 KINEM nonlinear TYPE Std'.format(shape, ' '.join([str(i) for i in range(1, nnodes+1)])), self.__get_nodes(nnodes))

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
