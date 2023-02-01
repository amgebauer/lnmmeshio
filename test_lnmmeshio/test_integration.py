import os
import unittest

import lnmmeshio
import numpy as np
from lnmmeshio import Fiber

script_dir = os.path.dirname(os.path.realpath(__file__))


class TestFibers(unittest.TestCase):
    def setUp(self):
        pass

    def test_tri3_integration(self):
        tri3 = lnmmeshio.Tri3(
            "T3",
            [
                lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
                lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
                lnmmeshio.Node(np.array([2.0, 3.0, 0.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1, 1), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1, 3), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri3.integrate_xi(lambda xi: 1.1, 1), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri3.integrate_xi(lambda xi: 1.1, 3), np.array(1.5 * 1.1)
        )

        tri3 = lnmmeshio.Tri3(
            "T3",
            [
                lnmmeshio.Node(np.array([0.0, 0.0, 1.0])),
                lnmmeshio.Node(np.array([1.0, 0.0, 4.0])),
                lnmmeshio.Node(np.array([2.0, 3.0, 5.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1, 1), np.array(5.3324478)
        )
        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1, 3), np.array(5.3324478)
        )

        np.testing.assert_almost_equal(
            tri3.integrate_xi(lambda xi: 1.1, 1), np.array(5.3324478)
        )
        np.testing.assert_almost_equal(
            tri3.integrate_xi(lambda xi: 1.1, 3), np.array(5.3324478)
        )

    def test_tri6_integration(self):
        tri6 = lnmmeshio.Tri6(
            "T6",
            [
                lnmmeshio.Node(np.array([0.0, 0.0, 0.0])),
                lnmmeshio.Node(np.array([1.0, 0.0, 0.0])),
                lnmmeshio.Node(np.array([2.0, 3.0, 0.0])),
                lnmmeshio.Node(np.array([0.5, 0.0, 0.0])),
                lnmmeshio.Node(np.array([1.5, 1.5, 0.0])),
                lnmmeshio.Node(np.array([1.0, 1.5, 0.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1, 1), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1, 3), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri6.integrate_xi(lambda xi: 1.1, 1), np.array(1.5 * 1.1)
        )
        np.testing.assert_almost_equal(
            tri6.integrate_xi(lambda xi: 1.1, 3), np.array(1.5 * 1.1)
        )

        tri6 = lnmmeshio.Tri6(
            "T6",
            [
                lnmmeshio.Node(np.array([0.0, 0.0, 1.0])),
                lnmmeshio.Node(np.array([1.0, 0.0, 4.0])),
                lnmmeshio.Node(np.array([2.0, 3.0, 5.0])),
                lnmmeshio.Node(np.array([0.5, 0.0, 2.5])),
                lnmmeshio.Node(np.array([1.5, 1.5, 4.5])),
                lnmmeshio.Node(np.array([1.0, 1.5, 3.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1, 1), np.array(5.3324478)
        )
        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1, 3), np.array(5.3324478)
        )
        np.testing.assert_almost_equal(
            tri6.integrate_xi(lambda xi: 1.1, 1), np.array(5.3324478)
        )
        np.testing.assert_almost_equal(
            tri6.integrate_xi(lambda xi: 1.1, 3), np.array(5.3324478)
        )

    def test_tri3_integration_x_xi(self):
        tri3 = lnmmeshio.Tri3(
            "T3",
            [
                lnmmeshio.Node(np.array([-1.0, -2.0, 0.0])),
                lnmmeshio.Node(np.array([2.0, -2.0, 0.0])),
                lnmmeshio.Node(np.array([-1.0, 2.0, 0.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1 * x[0] + 1.2 * x[1], 1), np.array(-4.8)
        )
        np.testing.assert_almost_equal(
            tri3.integrate(lambda x: 1.1 * x[0] + 1.2 * x[1], 3), np.array(-4.8)
        )

        np.testing.assert_almost_equal(
            tri3.integrate_xi(
                lambda xi: 1.1 * (3 * xi[0] - 1) + 1.2 * (4 * xi[1] - 2), 1
            ),
            np.array(-4.8),
        )
        np.testing.assert_almost_equal(
            tri3.integrate_xi(
                lambda xi: 1.1 * (3 * xi[0] - 1) + 1.2 * (4 * xi[1] - 2), 3
            ),
            np.array(-4.8),
        )

    def test_tri6_integration_x_xi(self):
        tri6 = lnmmeshio.Tri6(
            "T6",
            [
                lnmmeshio.Node(np.array([-1.0, -2.0, 0.0])),
                lnmmeshio.Node(np.array([2.0, -2.0, 0.0])),
                lnmmeshio.Node(np.array([-1.0, 2.0, 0.0])),
                lnmmeshio.Node(np.array([0.5, -2.0, 0.0])),
                lnmmeshio.Node(np.array([0.5, 0.0, 0.0])),
                lnmmeshio.Node(np.array([-1.0, 0.0, 0.0])),
            ],
        )

        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1 * x[0] + 1.2 * x[1], 1), np.array(-4.8)
        )
        np.testing.assert_almost_equal(
            tri6.integrate(lambda x: 1.1 * x[0] + 1.2 * x[1], 3), np.array(-4.8)
        )

        np.testing.assert_almost_equal(
            tri6.integrate_xi(
                lambda xi: 1.1 * (3 * xi[0] - 1) + 1.2 * (4 * xi[1] - 2), 1
            ),
            np.array(-4.8),
        )
        np.testing.assert_almost_equal(
            tri6.integrate_xi(
                lambda xi: 1.1 * (3 * xi[0] - 1) + 1.2 * (4 * xi[1] - 2), 3
            ),
            np.array(-4.8),
        )
