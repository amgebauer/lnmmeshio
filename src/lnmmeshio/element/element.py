import io
import math
from collections import OrderedDict
from typing import Dict, List, Optional, Union

import numpy as np

from ..fiber import Fiber
from ..ioutils import (
    line_option_list,
    read_option_item,
    write_option,
    write_option_list,
    write_title,
)
from ..node import Node


class Element:
    """
    Class holding the data of one element
    """

    def __init__(
        self,
        el_type: Optional[str],
        shape: str,
        nodes: List[Node],
        options: Optional[OrderedDict] = None,
    ):
        """
        Creates a new element of type ele_type, shape with nodes defined in nodes

        Args:
            el_type: str of element type as used by BACI (e.g. SOHEX8)
            shape: shape of the element as used by BACI (e.g. HEX8)
            nodes: List of node objects
        """
        self.id: Optional[int] = None
        self.type = el_type
        self.shape = shape
        self.nodes = nodes
        self.options = options if options is not None else OrderedDict()
        self.fibers: Dict[str, Fiber] = {}
        self.data: Dict[str, Union[np.ndarray, int, float]] = {}

    @classmethod
    def get_num_nodes(cls) -> int:
        """
        Get number of nodes of the element

        Returns:
            Number of nodes of the element
        """
        raise NotImplementedError("This method is not implemented in your element")

    def get_node_coords(self) -> np.ndarray:
        arr = np.zeros((self.get_num_nodes(), 3))

        for i, node in enumerate(self.nodes):
            arr[i, :] = node.coords

        return arr

    def reset(self):
        """
        Sets the element id to None
        """
        self.id = None

    def get_nodes(self) -> List[Node]:
        """
        Returns a list of nodes

        Returns:
            List of nodes
        """
        return self.nodes

    def get_faces(self) -> list:
        """
        Returns all faces

        Returns:
            List of faces
        """
        raise RuntimeError("This element does't implement get faces")

    def get_edges(self) -> list:
        """
        Returns all edges

        Returns:
            List of edges
        """
        raise RuntimeError("This element does't implement get edges")

    def get_node_ids(self):
        """
        Returns the node ids as of each element as a numpy array of shape (num_ele, num_nod_per_ele)

        Returns:
            np.array with node ids of each element
        """
        arr: np.ndarray = np.zeros((len(self.nodes)), dtype=int)

        for i, node in enumerate(self.nodes, start=0):
            if node.id is None:
                raise RuntimeError("You need to compute ids first")
            arr[i] = node.id

        return arr

    def get_dpoints(self):
        """
        Returns a list of dpoints that is shared by all nodes of the element

        Returns:
            List of dpoint
        """
        pointnodesets = None

        for p in self.nodes:
            if pointnodesets is None:
                pointnodesets = set(p.pointnodesets)
            else:
                pointnodesets = set(p.pointnodesets).intersection(pointnodesets)

        return list(pointnodesets)

    def get_dlines(self):
        """
        Returns a list of dlines that is shared by all nodes of the element

        Returns:
            List of dlines
        """
        linenodesets = None

        for p in self.nodes:
            if linenodesets is None:
                linenodesets = set(p.linenodesets)
            else:
                linenodesets = set(p.linenodesets).intersection(linenodesets)

        return list(linenodesets)

    def get_dsurfs(self):
        """
        Returns a list of dsurf that is shared by all nodes of the element

        Returns:
            List of dsurfs
        """
        surfacenodesets = None

        for p in self.nodes:
            if surfacenodesets is None:
                surfacenodesets = set(p.surfacenodesets)
            else:
                surfacenodesets = set(p.surfacenodesets).intersection(surfacenodesets)

        return list(surfacenodesets)

    def get_dvols(self):
        """
        Returns a list of dvol that is shared by all nodes of the element

        Returns:
            List of dvols
        """
        volumenodesets = None

        for p in self.nodes:
            if volumenodesets is None:
                volumenodesets = set(p.volumenodesets)
            else:
                volumenodesets = set(p.volumenodesets).intersection(volumenodesets)

        return list(volumenodesets)

    def get_line(self):
        line = io.StringIO()
        if self.id is None:
            raise RuntimeError("You have to compute ids before writing")

        line.write("{0} {1} ".format(self.id, self.type))

        options: OrderedDict = OrderedDict()
        options[self.shape] = [i.id for i in self.nodes]
        options.update(self.options)

        line.write(line_option_list(options))

        for t, f in self.fibers.items():
            line.write(" ")
            line.write(f.get_line(t))

        return line.getvalue()

    def write(self, dest):
        """
        Write the corresponding element line in the dat file
        """
        if self.id is None:
            raise RuntimeError("You have to compute ids before writing")

        dest.write("{0} {1} ".format(self.id, self.type))

        options: OrderedDict = OrderedDict()
        options[self.shape] = [i.id for i in self.nodes]
        options.update(self.options)

        write_option_list(dest, options, newline=False)

        for t, f in self.fibers.items():
            dest.write(" ")
            f.write(dest, t)

        dest.write("\n")

    @classmethod
    def get_space_dim(cls):
        """
        Returns the number of space dimensions

        Returns:
            Number of space dimensions
        """
        raise NotImplementedError(
            "This element is not correctly implemented. It needs to be derived from Element{1,2,3}D"
        )

    def get_xi(self, x):
        """
        Returns the local variables from given global variables

        Args:
            x: Global variable

        Returns:
            Local variables (xi)
        """
        raise NotImplementedError("This is currently not implemented for all elements")

    @classmethod
    def is_in_ref(cls, xi, include_boundary=True):
        """
        Checkes whether a point in reference coordinates is within the element

        Args:
            xi: Point in reference coordinates

        Returns:
            True if the point is within the element (or on the bounrary), otherwise False
        """
        raise NotImplementedError("This is currently not implemented for all elements")

    def is_in(self, x, include_boundary=True):
        """
        Check whether a point is within the element

        Args:
            x: Point in space
            include_boundary: bool, Whether or not to include the boundary

        Returns:
            True if the point is within the element (or on the boundary), otherwise False
        """
        return self.is_in_ref(self.get_xi(x))

    def project_quantity(self, x: np.ndarray, q: np.ndarray):
        """
        Projects the quantity from the nodal quantities q to the position x

        Args:
            x: Point in space
            q: Nodal values of the quantities

        Returns:
            q_x: Quantity at x projected with the shape functions
        """

        return self.project_quantity_xi(self.get_xi(x), q)

    def project_quantity_xi(self, xi: np.ndarray, q: np.ndarray):
        """
        Projects the quantity from the nodal quantities q to the local position in reference coordinates xi

        Args:
            xi: Point in the element in reference coordinates
            q: Nodal values of the quantities

        Returns:
            q_x: Quantity at xi projected with the shape functions
        """
        shapefcns = self.shape_fcns(xi)

        if q.shape[0] != self.get_num_nodes():
            raise ValueError(
                "Expecting nodal values of the quantities, expected {0} got {1}".format(
                    self.get_num_nodes(), q.shape[0]
                )
            )

        return np.dot(shapefcns, q)

    def integrate(self, integrand, numgp) -> np.ndarray:
        """
        Integrates the integrand over the element

        Args:
            integrand: integrand as a function of x
            numgp: Number of integration points to be used
        """
        raise NotImplementedError(
            "Integration is currently not implemented for all elements"
        )

    @classmethod
    def num_nodes_by_shape(cls, shape: str):
        """
        Returns the number of nodes from the shapes

        Args:
            shape: shape as used in baci .dat file format

        Returngs:
            int: number of nodes
        """
        shape_dict = {
            "VERTEX1": 1,
            "TET4": 4,
            "TET10": 10,
            "PYRAMID5": 5,
            "HEX8": 8,
            "HEX20": 20,
            "HEX27": 27,
            "WEDGE6": 6,
            "QUAD4": 4,
            "TRI3": 3,
            "TRI6": 6,
            "LINE2": 2,
            "LINE3": 3,
            "QUAD8": 8,
            "QUAD9": 9,
        }

        if shape not in shape_dict:
            raise ValueError("Element of shape {0} is unknown".format(shape))

        return shape_dict[shape]

    @classmethod
    def shape_fcns(cls, xi):
        """
        Returns the value of the shape functions at the local coordinate xi
        """
        raise NotImplementedError("This element has not implemented shape functions")

    @classmethod
    def int_points(cls, num_points):
        """
        Returns the position of the integration points for a given number of integration points
        """
        raise NotImplementedError("This element has not implemented integration points")


class Element0D(Element):
    @classmethod
    def get_space_dim(cls):
        """
        Returns the number of space dimensions

        Returns:
            Number of space dimensions
        """
        return 0


class Element1D(Element):
    @classmethod
    def get_space_dim(cls):
        """
        Returns the number of space dimensions

        Returns:
            Number of space dimensions
        """
        return 1


class Element2D(Element):
    @classmethod
    def get_space_dim(cls):
        """
        Returns the number of space dimensions

        Returns:
            Number of space dimensions
        """
        return 2


class Element3D(Element):
    @classmethod
    def get_space_dim(cls):
        """
        Returns the number of space dimensions

        Returns:
            Number of space dimensions
        """
        return 3


class ElementTri(Element2D):
    @classmethod
    def int_points(cls, num_points: int) -> np.ndarray:
        """
        Returns the position of the integration points for a given number of integration points
        """
        if num_points == 1:
            return np.array([[1.0 / 3.0, 1.0 / 3.0]])
        if num_points == 3:
            return np.array(
                [[1.0 / 6.0, 1.0 / 6.0], [2.0 / 3.0, 1.0 / 6.0], [1.0 / 6.0, 2.0 / 3.0]]
            )
        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for TRI elements".format(
                num_points
            )
        )

    @classmethod
    def int_weights(cls, num_points: int) -> np.ndarray:
        if num_points == 1:
            return np.array([0.5])
        elif num_points == 3:
            return np.array([1.0 / 6.0, 1.0 / 6.0, 1.0 / 6.0])
        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for TRI elements".format(
                num_points
            )
        )


class ElementQuad(Element2D):
    @classmethod
    def int_weights(cls, num_points: int) -> np.ndarray:
        """
        Returns the integration weights for the integration points
        """
        if num_points == 1:
            return np.array([2])
        elif num_points == 4:
            return np.array([1.0, 1.0, 1.0, 1.0])

        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for TET elements".format(
                num_points
            )
        )

    @classmethod
    def int_points(cls, num_points: int) -> np.ndarray:
        """
        Returns the position of the integration points for a given number of integration points
        """
        if num_points == 1:
            return np.array([[0.0, 0.0]])
        if num_points == 4:
            return np.array(
                [
                    [-0.5773502691896, -0.5773502691896],
                    [0.5773502691896, -0.5773502691896],
                    [-0.5773502691896, 0.5773502691896],
                    [0.5773502691896, 0.5773502691896],
                ]
            )
        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for TET elements".format(
                num_points
            )
        )


class ElementTet(Element3D):
    @classmethod
    def is_in_ref(cls, xi, include_boundary=True):
        if include_boundary:

            def lop(x, y):
                return x >= y

        else:

            def lop(x, y):
                return x > y

        if not all([lop(xi[i], 0) for i in range(3)]):
            return False

        if not lop(1, xi[0]):
            return False

        if not lop(1 - xi[0], xi[1]):
            return False

        if not lop(1 - xi[0] - xi[1], xi[2]):
            return False

        return True

    @classmethod
    def int_weights(cls, num_points):
        """
        Returns the integration weights for the integration points
        """
        if num_points == 1:
            return np.array([1.0 / 6.0])
        elif num_points == 4:
            return np.array(
                [1.0 / 6.0 / 4.0, 1.0 / 6.0 / 4.0, 1.0 / 6.0 / 4.0, 1.0 / 6.0 / 4.0]
            )

    @classmethod
    def int_points(cls, num_points):
        """
        Returns the position of the integration points for a given number of integration points
        """
        if num_points == 1:
            return np.array([0.25, 0.25, 0.25])
        if num_points == 4:
            palpha = (5.0 + 3.0 * math.sqrt(5.0)) / 20.0
            pbeta = (5.0 - math.sqrt(5.0)) / 20.0

            return np.array(
                [
                    [pbeta, pbeta, pbeta],
                    [palpha, pbeta, pbeta],
                    [pbeta, palpha, pbeta],
                    [pbeta, pbeta, palpha],
                ]
            )
        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for TET elements".format(
                num_points
            )
        )


class ElementHex(Element3D):
    @classmethod
    def is_in_ref(cls, xi, include_boundary=True):
        if include_boundary:

            def lop(x, y):
                return x >= y

        else:

            def lop(x, y):
                return x > y

        if not all([lop(xi[i], -1.0) for i in range(3)]):
            return False

        if not all([lop(1.0, xi[i]) for i in range(3)]):
            return False

        return True

    @classmethod
    def int_points(cls, num_points):
        """
        Returns the position of the integration points for a given number of integration points
        """
        if num_points == 8:
            xi = 1.0 / math.sqrt(3.0)

            return (
                np.array(
                    [
                        [-1, -1, -1],
                        [1, -1, -1],
                        [1, 1, -1],
                        [-1, 1, -1],
                        [-1, -1, 1],
                        [1, -1, 1],
                        [1, 1, 1],
                        [-1, 1, 1],
                    ]
                )
                * xi
            )
        raise RuntimeError(
            "The number of integration points provided ({0}) is not supported for HEX elements".format(
                num_points
            )
        )

    @classmethod
    def int_weights(cls, num_points):
        """
        Returns the integration weights for the integration points
        """
        if num_points == 8:
            return np.ones(8)
