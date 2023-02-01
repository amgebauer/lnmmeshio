import os
import unittest

import numpy as np
import sympy as sp
from lnmmeshio import (
    Element,
    Element1D,
    Element2D,
    Element3D,
    Hex8,
    Hex20,
    Hex27,
    Line2,
    Line3,
    Quad4,
    Quad8,
    Quad9,
    Tet4,
    Tet10,
    Tri3,
    Tri6,
    Vertex,
)
from lnmmeshio.element.parse_element import parse as parse_ele
from lnmmeshio.node import Node
from lnmmeshio.nodeset import LineNodeset, PointNodeset, SurfaceNodeset, VolumeNodeset
from parameterized import parameterized

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestEles(unittest.TestCase):
    def setUp(self):
        pass

    def __get_nodes(self, n):
        nodes = [Node(np.random.rand(3)) for i in range(n)]

        for i, n in enumerate(nodes):
            n.id = i

        return nodes

    def test_common(self):
        ele = Element(None, "X", self.__get_nodes(3))

        vnds = [VolumeNodeset(0), VolumeNodeset(1), VolumeNodeset(2), VolumeNodeset(3)]
        snds = [
            SurfaceNodeset(10),
            SurfaceNodeset(11),
            SurfaceNodeset(12),
            SurfaceNodeset(13),
        ]
        lnds = [LineNodeset(20), LineNodeset(21), LineNodeset(22), LineNodeset(23)]
        pnds = [PointNodeset(30), PointNodeset(31), PointNodeset(32), PointNodeset(33)]

        for i in [0, 1, 2, 3]:
            vnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]:
            vnds[i].add_node(ele.nodes[1])
        for i in [0, 1]:
            vnds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]:
            snds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]:
            snds[i].add_node(ele.nodes[1])
        for i in [0, 1]:
            snds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]:
            lnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]:
            lnds[i].add_node(ele.nodes[1])
        for i in [0, 1]:
            lnds[i].add_node(ele.nodes[2])

        for i in [0, 1, 2, 3]:
            pnds[i].add_node(ele.nodes[0])
        for i in [0, 1, 2]:
            pnds[i].add_node(ele.nodes[1])
        for i in [0, 1]:
            pnds[i].add_node(ele.nodes[2])

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

        for i, n in enumerate(ele.nodes):
            n.id = i

        self.assertListEqual(list(ele.get_node_ids()), list(range(0, 3)))

    def __test_shape_functions_sum(self, ele):
        # check whether the sum of all shape functions is 1 everywhere
        if issubclass(ele, Element1D):
            xi = sp.symbols("xi_1")
        elif issubclass(ele, Element2D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2")])
        elif issubclass(ele, Element3D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2"), sp.symbols("xi_3")])
        else:
            raise NotImplementedError("Unknown number of dimension: {0}".format(ele))
        shapefcns = ele.shape_fcns(xi)

        self.assertEqual(sp.simplify(sum(shapefcns)), 1)

    @staticmethod
    def _subs(expr, x, y):
        if not hasattr(expr, "shape"):
            myexpr = expr
            for xi, yi in zip(x, y):
                myexpr = myexpr.subs(xi, yi)

            return myexpr

        out = np.zeros(expr.shape, dtype=expr.dtype)

        for index in np.ndindex(expr.shape):
            out[index] = expr[index]
            for xi, yi in zip(x, y):
                out[index] = out[index].subs(xi, yi)

        return out

    def __test_nodal_reference_coordinates(self, ele):
        # check whether all shape functions are 0 except the one of the reference coordinates
        if issubclass(ele, Element1D):
            xi = sp.symbols("xi_1")
        elif issubclass(ele, Element2D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2")])
        elif issubclass(ele, Element3D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2"), sp.symbols("xi_3")])
        else:
            raise NotImplementedError("Unknown number of dimension: {0}".format(ele))

        shapefcns = ele.shape_fcns(xi)
        for i, ref_coords in enumerate(ele.nodal_reference_coordinates()):
            for j, shapefcn in enumerate(shapefcns):
                self.assertEqual(
                    sp.simplify(self._subs(shapefcn, xi, ref_coords)),
                    1 if i == j else 0,
                )

    def __test_point_in_ref(self, cls):
        self.assertTrue(cls.is_in_ref(np.array([0.1, 0.1, 0.1])))
        self.assertTrue(cls.is_in_ref(np.array([1.0, 0.0, 0.0])))
        self.assertTrue(cls.is_in_ref(np.array([1.0, 0.0, 0.0]), include_boundary=True))
        self.assertFalse(
            cls.is_in_ref(np.array([1.0, 0.0, 0.0]), include_boundary=False)
        )
        self.assertFalse(cls.is_in_ref(np.array([-100, -100, -100])))

    def __test_ele(
        self, shape, cls, nnodes, faces, facetype, edges, edgetype, test_get_xi=False
    ):
        ele = parse_ele(
            "1 ELENAME {0} {1} MAT 11 KINEM nonlinear TYPE Std".format(
                shape, " ".join([str(i) for i in range(1, nnodes + 1)])
            ),
            self.__get_nodes(nnodes),
        )

        self.assertEqual(int(ele.options["MAT"]), 11)

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
                self.assertEqual(
                    n.id, edges[i][j], "Error at edge {0} (node {1})".format(i, j)
                )

        if test_get_xi:
            coords = np.transpose(np.array([n.coords for n in ele.nodes]))
            for _ in range(100):
                xi = np.random.rand((3))

                # transform x to xi
                x = np.dot(coords, ele.shape_fcns(xi))

                # transform x to xi
                xi2 = ele.get_xi(x)

                # compare
                for a, b in zip(xi, xi2):
                    self.assertAlmostEqual(a, b)

    def _test_ele_shpfcns(self, cls, xis):
        for i, xi in enumerate(xis):
            if not isinstance(xi, np.ndarray):
                xis[i] = np.array(xi).reshape((-1))

        ndim = xis[0].shape[0]
        xi_minmax = np.full((ndim, 2), np.nan)
        for i, xi in enumerate(xis):
            shpfcns = cls.shape_fcns(xi)

            cmp_vct = np.zeros((len(shpfcns)), dtype=float)
            cmp_vct[i] = 1.0

            self.assertListEqual(
                list(shpfcns),
                list(cmp_vct),
                "Shapefunctions differ at {0} / xi={1}".format(i, xi),
            )

            for k, xij in enumerate(xi):
                if np.isnan(xi_minmax[k][0]) or xi_minmax[k][0] > xij:
                    xi_minmax[k][0] = xij
                if np.isnan(xi_minmax[k][1]) or xi_minmax[k][1] < xij:
                    xi_minmax[k][1] = xij

        constant = np.nan
        for _ in range(1000):
            r = np.random.rand(ndim)

            cur_result = np.sum(cls.shape_fcns(r))

            if np.isnan(constant):
                constant = cur_result
            else:
                self.assertAlmostEqual(constant, cur_result)

    @parameterized.expand(
        [
            [Hex8],
            [Hex20],
            [Hex27],
            [Tet4],
            [Tet10],
            [Line2],
            [Line3],
            [Quad4],
            [Quad8],
            [Quad9],
            [Tri3],
            [Tri6],
        ]
    )
    def test_shape_fcns(self, ele):
        self.__test_shape_functions_sum(ele)

    @parameterized.expand(
        [
            [Hex8],
            [Tet4],
            [Tet10],
            [Line2],
            [Quad4],
            [Tri3],
            [Tri6],
        ]
    )
    def test_shape_fcns_derivs(self, ele):
        # check whether the sum of all shape functions is 1 everywhere
        if issubclass(ele, Element1D):
            xi = sp.symbols("xi_1")
            num_xis = 1
        elif issubclass(ele, Element2D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2")])
            num_xis = 2
        elif issubclass(ele, Element3D):
            xi = np.array([sp.symbols("xi_1"), sp.symbols("xi_2"), sp.symbols("xi_3")])
            num_xis = 3
        else:
            raise NotImplementedError("Unknown number of dimension: {0}".format(ele))
        shapefcns = ele.shape_fcns(xi)
        shapefcnsderivs = ele.shape_fcns_derivs(xi).reshape(num_xis, -1)
        for i in range(num_xis):
            # compute symbolic derivative
            for n in range(ele.get_num_nodes()):
                analytic_deriv = sp.diff(shapefcns[n], xi[i] if num_xis > 1 else xi)
                self.assertTrue(
                    sp.simplify(shapefcnsderivs[i, n] - analytic_deriv) == 0
                )

    @parameterized.expand(
        [
            [Hex8, 3],
            [Hex20, 3],
            [Hex27, 3],
            [Tet4, 3],
            [Tet10, 3],
            [Line2, 1],
            [Line3, 1],
            [Quad4, 2],
            [Quad8, 2],
            [Quad9, 2],
            [Tri3, 2],
            [Tri6, 2],
        ]
    )
    def test_space_dim(self, ele, dim):
        self.assertEqual(ele.get_space_dim(), dim)

    @parameterized.expand(
        [
            [Hex8],
            [Tet4],
            [Tet10],
        ]
    )
    def test_nodal_reference_coordinates(self, ele):
        self.__test_nodal_reference_coordinates(ele)

    @parameterized.expand(
        [
            [Hex8],
            [Hex20],
            [Hex27],
            [Tet4],
            [Tet10],
        ]
    )
    def test_is_in_ref(self, ele):
        self.__test_point_in_ref(ele)

    def test_hex8(self):
        FACES = [
            [0, 1, 2, 3],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
            [4, 5, 6, 7],
        ]
        EDGES = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
        ]

        # test ele
        self.__test_ele("HEX8", Hex8, 8, FACES, Quad4, EDGES, Line2)
        self._test_ele_shpfcns(
            Hex8,
            [
                np.array([-1.0, -1.0, -1.0]),
                np.array([1.0, -1.0, -1.0]),
                np.array([1.0, 1.0, -1.0]),
                np.array([-1.0, 1.0, -1.0]),
                np.array([-1.0, -1.0, 1.0]),
                np.array([1.0, -1.0, 1.0]),
                np.array([1.0, 1.0, 1.0]),
                np.array([-1.0, 1.0, 1.0]),
            ],
        )

    def test_hex20(self):
        FACES = [
            [0, 1, 2, 3, 8, 9, 10, 11],
            [0, 1, 5, 4, 8, 13, 16, 12],
            [1, 2, 6, 5, 9, 14, 17, 13],
            [2, 3, 7, 6, 10, 15, 18, 14],
            [3, 0, 4, 7, 11, 12, 19, 15],
            [4, 5, 6, 7, 15, 17, 18, 19],
        ]
        EDGES = [
            [0, 1, 8],
            [1, 2, 9],
            [2, 3, 10],
            [3, 0, 11],
            [0, 4, 12],
            [1, 5, 13],
            [2, 6, 14],
            [3, 7, 15],
            [4, 5, 16],
            [5, 6, 17],
            [6, 7, 18],
            [7, 4, 19],
        ]

        # test ele
        self.__test_ele("HEX20", Hex20, 20, FACES, Quad8, EDGES, Line3)
        self._test_ele_shpfcns(
            Hex20,
            [
                np.array([-1.0, -1.0, -1.0]),
                np.array([1.0, -1.0, -1.0]),
                np.array([1.0, 1.0, -1.0]),
                np.array([-1.0, 1.0, -1.0]),
                np.array([-1.0, -1.0, 1.0]),
                np.array([1.0, -1.0, 1.0]),
                np.array([1.0, 1.0, 1.0]),
                np.array([-1.0, 1.0, 1.0]),
                np.array([0.0, -1.0, -1.0]),
                np.array([1.0, 0.0, -1.0]),
                np.array([0.0, 1.0, -1.0]),
                np.array([-1.0, 0.0, -1.0]),
                np.array([-1.0, -1.0, 0.0]),
                np.array([1.0, -1.0, 0.0]),
                np.array([1.0, 1.0, 0.0]),
                np.array([-1.0, 1.0, 0.0]),
                np.array([0.0, -1.0, 1.0]),
                np.array([1.0, 0.0, 1.0]),
                np.array([0.0, 1.0, 1.0]),
                np.array([-1.0, 0.0, 1.0]),
            ],
        )

    def test_hex27(self):
        FACES = [
            [0, 1, 2, 3, 8, 9, 10, 11, 20],
            [0, 1, 5, 4, 8, 13, 16, 12, 21],
            [1, 2, 6, 5, 9, 14, 17, 13, 22],
            [2, 3, 7, 6, 10, 15, 18, 14, 23],
            [3, 0, 4, 7, 11, 12, 19, 15, 24],
            [4, 5, 6, 7, 15, 17, 18, 19, 25],
        ]
        EDGES = [
            [0, 1, 8],
            [1, 2, 9],
            [2, 3, 10],
            [3, 0, 11],
            [0, 4, 12],
            [1, 5, 13],
            [2, 6, 14],
            [3, 7, 15],
            [4, 5, 16],
            [5, 6, 17],
            [6, 7, 18],
            [7, 4, 19],
        ]

        self.__test_ele("HEX27", Hex27, 27, FACES, Quad9, EDGES, Line3)
        self._test_ele_shpfcns(
            Hex27,
            [
                np.array([-1.0, -1.0, -1.0]),
                np.array([1.0, -1.0, -1.0]),
                np.array([1.0, 1.0, -1.0]),
                np.array([-1.0, 1.0, -1.0]),
                np.array([-1.0, -1.0, 1.0]),
                np.array([1.0, -1.0, 1.0]),
                np.array([1.0, 1.0, 1.0]),
                np.array([-1.0, 1.0, 1.0]),
                np.array([0.0, -1.0, -1.0]),
                np.array([1.0, 0.0, -1.0]),
                np.array([0.0, 1.0, -1.0]),
                np.array([-1.0, 0.0, -1.0]),
                np.array([-1.0, -1.0, 0.0]),
                np.array([1.0, -1.0, 0.0]),
                np.array([1.0, 1.0, 0.0]),
                np.array([-1.0, 1.0, 0.0]),
                np.array([0.0, -1.0, 1.0]),
                np.array([1.0, 0.0, 1.0]),
                np.array([0.0, 1.0, 1.0]),
                np.array([-1.0, 0.0, 1.0]),
                np.array([0.0, 0.0, -1.0]),
                np.array([0.0, -1.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([-1.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.0, 0.0, 0.0]),
            ],
        )

    def test_tet10(self):
        FACES = [
            [0, 1, 3, 4, 8, 7],
            [1, 2, 3, 5, 9, 8],
            [2, 0, 3, 6, 7, 9],
            [0, 2, 1, 6, 5, 4],
        ]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 0, 6], [0, 3, 7], [1, 3, 8], [2, 3, 9]]

        # parse
        self.__test_ele("TET10", Tet10, 10, FACES, Tri6, EDGES, Line3)
        self._test_ele_shpfcns(
            Tet10,
            [
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
                np.array([0.5, 0.0, 0.0]),
                np.array([0.5, 0.5, 0.0]),
                np.array([0.0, 0.5, 0.0]),
                np.array([0.0, 0.0, 0.5]),
                np.array([0.5, 0.0, 0.5]),
                np.array([0.0, 0.5, 0.5]),
            ],
        )

    def test_tet4(self):
        FACES = [[0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1]]
        EDGES = [[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]]

        # parse
        self.__test_ele("TET4", Tet4, 4, FACES, Tri3, EDGES, Line2, test_get_xi=True)
        self._test_ele_shpfcns(
            Tet4,
            [
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]),
            ],
        )
        # test project quantity
        ele = Tet4(
            "",
            [
                Node(np.array([0.1, 0.2, 0.3])),
                Node(np.array([1.2, 0.3, 0.4])),
                Node(np.array([0.1, 2.2, 0.3])),
                Node(np.array([0.1, 0.22, 1.2])),
            ],
        )

        noddata = np.array([[0.1, 0.2], [0.2, 0.3], [0.3, 0.4], [0.4, 0.5]])

        for i in range(4):
            n1 = ele.nodes[i]
            q1 = noddata[i]
            for j in range(4):
                n2 = ele.nodes[j]
                q2 = noddata[j]

                for xi in np.linspace(0, 1, 10):
                    pos = n1.coords + xi * (n2.coords - n1.coords)
                    qxi = q1 + xi * (q2 - q1)

                    qxi_proj = ele.project_quantity(pos, noddata)

                    for i in range(len(qxi)):
                        self.assertAlmostEqual(qxi_proj[i], qxi[i])

    def test_quad4(self):
        FACES = [[0, 1, 2, 3]]
        EDGES = [[0, 1], [1, 2], [2, 3], [3, 0]]

        # parse
        self.__test_ele("QUAD4", Quad4, 4, FACES, Quad4, EDGES, Line2)
        self._test_ele_shpfcns(
            Quad4,
            [
                np.array([-1.0, -1.0]),
                np.array([1.0, -1.0]),
                np.array([1.0, 1.0]),
                np.array([-1.0, 1.0]),
            ],
        )

    def test_quad8(self):
        FACES = [[0, 1, 2, 3, 4, 5, 6, 7, 8]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 3, 6], [3, 0, 7]]

        self.__test_ele("QUAD8", Quad8, 8, FACES, Quad8, EDGES, Line3)
        self._test_ele_shpfcns(
            Quad8,
            [
                np.array([-1.0, -1.0]),
                np.array([1.0, -1.0]),
                np.array([1.0, 1.0]),
                np.array([-1.0, 1.0]),
                np.array([0.0, -1.0]),
                np.array([1.0, 0.0]),
                np.array([0.0, 1.0]),
                np.array([-1.0, 0.0]),
            ],
        )

    def test_quad9(self):
        FACES = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        EDGES = [[0, 1, 4], [1, 2, 5], [2, 3, 6], [3, 0, 7]]

        self.__test_ele("QUAD9", Quad9, 9, FACES, Quad9, EDGES, Line3)
        self._test_ele_shpfcns(
            Quad9,
            [
                np.array([-1.0, -1.0]),
                np.array([1.0, -1.0]),
                np.array([1.0, 1.0]),
                np.array([-1.0, 1.0]),
                np.array([0.0, -1.0]),
                np.array([1.0, 0.0]),
                np.array([0.0, 1.0]),
                np.array([-1.0, 0.0]),
                np.array([0.0, 0.0]),
            ],
        )

    def test_tri3(self):
        FACES = [[0, 1, 2]]
        EDGES = [[0, 1], [1, 2], [2, 0]]

        self.__test_ele("TRI3", Tri3, 3, FACES, Tri3, EDGES, Line2)
        self._test_ele_shpfcns(
            Tri3, [np.array([0.0, 0.0]), np.array([1.0, 0.0]), np.array([0.0, 1.0])]
        )

    def test_tri6(self):
        FACES = [[0, 1, 2, 3, 4, 5]]
        EDGES = [[0, 1, 3], [1, 2, 4], [2, 0, 5]]

        self.__test_ele("TRI6", Tri6, 6, FACES, Tri6, EDGES, Line3)
        self._test_ele_shpfcns(
            Tri6,
            [
                np.array([0.0, 0.0]),
                np.array([1.0, 0.0]),
                np.array([0.0, 1.0]),
                np.array([0.5, 0.0]),
                np.array([0.5, 0.5]),
                np.array([0.0, 0.5]),
            ],
        )

    def test_line2(self):
        EDGES = [[0, 1]]

        self.__test_ele("LINE2", Line2, 2, [], None, EDGES, Line2)
        self._test_ele_shpfcns(Line2, [-1.0, 1.0])

    def test_line3(self):
        EDGES = [[0, 1, 2]]

        self.__test_ele("LINE3", Line3, 3, [], None, EDGES, Line3)
        self._test_ele_shpfcns(Line3, [-1.0, 1.0, 0.0])

    def test_vertex1(self):
        self.__test_ele("VERTEX1", Vertex, 1, [], None, [], None)
