import re
from typing import List, Optional

from ..fiber import Fiber
from ..ioutils import (
    read_key_values,
    read_option_items,
    write_option,
    write_option_list,
    write_title,
)
from ..node import Node
from .element import Element
from .hex8 import Hex8
from .hex20 import Hex20
from .hex27 import Hex27
from .line2 import Line2
from .line3 import Line3
from .quad4 import Quad4
from .quad8 import Quad8
from .quad9 import Quad9
from .tet4 import Tet4
from .tet10 import Tet10
from .tri3 import Tri3
from .tri6 import Tri6
from .vertex import Vertex

RegExEle = re.compile(r"^[ ]*([0-9]+)[ ]+(\S+)[ ]+(\S+)[ ]+")


def create_element(
    ele_type: str, ele_shape: str, ele_nodes: List[Node], throw_if_unknown=False
) -> Element:
    """
    Creates an element from a given element shape

    Args:
        elename: name of the element (e.g. SOLIDH8)
        shape: str shape of the element (e.g. HEX8)
        nodes: nodes of the element
        throw_if_unknown: bool Throw an exception, if element type is not known

    Return:
        Element of the specific type
    """

    ele: Optional[Element] = None
    if ele_shape == Vertex.ShapeName:
        ele = Vertex(ele_type, ele_nodes)
    elif ele_shape == Line2.ShapeName:
        ele = Line2(ele_type, ele_nodes)
    elif ele_shape == Line3.ShapeName:
        ele = Line3(ele_type, ele_nodes)
    elif ele_shape == Tri3.ShapeName:
        ele = Tri3(ele_type, ele_nodes)
    elif ele_shape == Tri6.ShapeName:
        ele = Tri6(ele_type, ele_nodes)
    elif ele_shape == Quad4.ShapeName:
        ele = Quad4(ele_type, ele_nodes)
    elif ele_shape == Quad8.ShapeName:
        ele = Quad8(ele_type, ele_nodes)
    elif ele_shape == Quad9.ShapeName:
        ele = Quad9(ele_type, ele_nodes)
    elif ele_shape == Tet4.ShapeName:
        ele = Tet4(ele_type, ele_nodes)
    elif ele_shape == Tet10.ShapeName:
        ele = Tet10(ele_type, ele_nodes)
    elif ele_shape == Hex8.ShapeName:
        ele = Hex8(ele_type, ele_nodes)
    elif ele_shape == Hex20.ShapeName:
        ele = Hex20(ele_type, ele_nodes)
    elif ele_shape == Hex27.ShapeName:
        ele = Hex27(ele_type, ele_nodes)
    else:
        if throw_if_unknown:
            raise RuntimeError("The element type {0} is unknown".format(ele_shape))
        ele = Element(ele_type, ele_shape, ele_nodes)

    return ele


def parse(line: str, nodes: List[Node], throw_if_unknown=False):
    """
    Parses the element and returns an instance of an appropriate element type

    Args:
        line: linedefinition of the element
        nodes: List of nodes

    Returns:
        An instance of the properly instantianted element
    """
    line = line.split("//", 1)[0]
    # parse ele id, type and shape
    ele_match = RegExEle.search(line)
    if not ele_match:
        return None

    ele_id = int(ele_match.group(1))
    ele_type = ele_match.group(2)
    ele_shape = ele_match.group(3)

    node_ids_str, span = read_option_items(
        line, ele_shape, Element.num_nodes_by_shape(ele_shape)
    )
    ele_nodes = [nodes[int(i) - 1] for i in node_ids_str]

    ele = create_element(
        ele_type, ele_shape, ele_nodes, throw_if_unknown=throw_if_unknown
    )

    ele.id = ele_id

    # read fibers
    ele.fibers = Fiber.parse_fibers(line)

    # read remaining options
    # assume only one value per option, which must not be the case in general
    line = line[span[1] :]

    for key, values in read_key_values(
        line, lambda key: 3 if Fiber.is_fiber_type(key) else 1
    ):
        if len(values) == 1:
            ele.options[key] = values[0]
        else:
            ele.options[key] = values

    return ele
