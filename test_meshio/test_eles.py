import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List
from lnmmeshio.element.parse_element import parse as parse_ele
from lnmmeshio.node import Node
from lnmmeshio.element.hex8 import Hex8
from lnmmeshio.element.tet10 import Tet10
from lnmmeshio.element.tet4 import Tet4
from lnmmeshio.element.quad4 import Quad4
from lnmmeshio.element.tri3 import Tri3
from lnmmeshio.element.tri6 import Tri6
from lnmmeshio.element.line2 import Line2
from lnmmeshio.element.line3 import Line3
from lnmmeshio.element.element import Element

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

    def test_hex8(self):
        FACES = [[0, 1, 2, 3], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
        EDGES = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4]]
        
        # parse
        ele = parse_ele('1 ELENAME HEX8 1 2 3 4 5 6 7 8 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(8))

        # test shape
        self.assertEqual(ele.shape, Hex8.ShapeName)
        self.assertEqual(ele.shape, 'HEX8')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 8)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 6)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Quad4.ShapeName)
            self.assertEqual(face.shape, 'QUAD4')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 12)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line2.ShapeName)
            self.assertEqual(edge.shape, 'LINE2')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_tet10(self):
        FACES = [[0, 1, 3, 4, 8, 7], [1, 2, 3, 5, 9, 8], [2, 0, 3, 6, 7, 9], [0, 2, 1, 6, 5, 4]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 0, 6], [0, 3, 7], [1, 3, 8], [2, 3, 9]]
        
        # parse
        ele = parse_ele('1 ELENAME TET10 1 2 3 4 5 6 7 8 9 10 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(10))

        # test shape
        self.assertEqual(ele.shape, Tet10.ShapeName)
        self.assertEqual(ele.shape, 'TET10')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 10)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 4)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Tri6.ShapeName)
            self.assertEqual(face.shape, 'TRI6')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 6)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line3.ShapeName)
            self.assertEqual(edge.shape, 'LINE3')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_tet4(self):
        FACES = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]
        EDGES = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]]
        
        # parse
        ele = parse_ele('1 ELENAME TET4 1 2 3 4 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(4))

        # test shape
        self.assertEqual(ele.shape, Tet4.ShapeName)
        self.assertEqual(ele.shape, 'TET4')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 4)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 4)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Tri3.ShapeName)
            self.assertEqual(face.shape, 'TRI3')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 6)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line2.ShapeName)
            self.assertEqual(edge.shape, 'LINE2')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_quad4(self):
        FACES = [[0, 1, 2, 3]]
        EDGES = [[0, 1], [1, 2], [2, 3], [3, 0]]
        
        # parse
        ele = parse_ele('1 ELENAME QUAD4 1 2 3 4 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(4))

        # test shape
        self.assertEqual(ele.shape, Quad4.ShapeName)
        self.assertEqual(ele.shape, 'QUAD4')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 4)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 1)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Quad4.ShapeName)
            self.assertEqual(face.shape, 'QUAD4')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 4)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line2.ShapeName)
            self.assertEqual(edge.shape, 'LINE2')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_tri3(self):
        FACES = [[0, 1, 2]]
        EDGES = [[0, 1], [1, 2], [2, 0]]
        
        # parse
        ele = parse_ele('1 ELENAME TRI3 1 2 3 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(3))

        # test shape
        self.assertEqual(ele.shape, Tri3.ShapeName)
        self.assertEqual(ele.shape, 'TRI3')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 3)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 1)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Tri3.ShapeName)
            self.assertEqual(face.shape, 'TRI3')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 3)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line2.ShapeName)
            self.assertEqual(edge.shape, 'LINE2')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_tri6(self):
        FACES = [[0, 1, 2, 3, 4, 5]]
        EDGES = [[0, 1, 3], [1, 2, 4], [2, 0, 5]]
        
        # parse
        ele = parse_ele('1 ELENAME TRI6 1 2 3 4 5 6 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(6))

        # test shape
        self.assertEqual(ele.shape, Tri6.ShapeName)
        self.assertEqual(ele.shape, 'TRI6')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 6)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 1)
        for i, face in enumerate(faces):
            self.assertEqual(face.shape, Tri6.ShapeName)
            self.assertEqual(face.shape, 'TRI6')

            # check if faces and nodes are ordered correctly
            for j, n in enumerate(face.get_nodes()):
                self.assertEqual(n.id, FACES[i][j])

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 3)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line3.ShapeName)
            self.assertEqual(edge.shape, 'LINE3')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))


    def test_line2(self):
        EDGES = [[0, 1]]
        
        # parse
        ele = parse_ele('1 ELENAME LINE2 1 2 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(2))

        # test shape
        self.assertEqual(ele.shape, Line2.ShapeName)
        self.assertEqual(ele.shape, 'LINE2')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 2)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 0)

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 1)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line2.ShapeName)
            self.assertEqual(edge.shape, 'LINE2')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))

    def test_line3(self):
        EDGES = [[0, 1, 2]]
        
        # parse
        ele = parse_ele('1 ELENAME LINE3 1 2 3 MAT 1 KINEM nonlinear TYPE Std', self.__get_nodes(3))

        # test shape
        self.assertEqual(ele.shape, Line3.ShapeName)
        self.assertEqual(ele.shape, 'LINE3')

        self.assertEqual(ele.get_num_nodes(), len(ele.nodes))
        self.assertEqual(ele.get_num_nodes(), 3)

        # test faces
        faces = ele.get_faces()
        self.assertEqual(len(faces), 0)

        # test edges
        edges = ele.get_edges()
        self.assertEqual(len(edges), 1)
        for i, edge in enumerate(edges):
            self.assertEqual(edge.shape, Line3.ShapeName)
            self.assertEqual(edge.shape, 'LINE3')


            # check if faces and nodes are ordered correctly
            for j, n in enumerate(edge.get_nodes()):
                self.assertEqual(n.id, EDGES[i][j], 'Error at edge {0} (node {1})'.format(i, j))
