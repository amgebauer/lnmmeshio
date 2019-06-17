from ..ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from typing import List
from .element import Element
from .line2 import Line2
from .line3 import Line3
from .tri3 import Tri3
from .tri6 import Tri6
from .quad4 import Quad4
from .tet4 import Tet4
from .tet10 import Tet10
from .hex8 import Hex8
import re
from ..fiber import Fiber
from ..node import Node


RegExEle = re.compile(r'^[ ]*([0-9]+)[ ]+(\S+)[ ]+(\S+)[ ]+')

"""
Parses the element and returns an instance of an appropriate element type

Args:
    line: linedefinition of the element
    nodes: List of nodes

Returns:
    An instance of the properly instantianted element
"""
def parse(line: str, nodes: List[Node]):
    line = line.split('//', 1)[0]
    # parse ele id, type and shape
    ele_match = RegExEle.search(line)
    if not ele_match:
        return None

    ele_id = int(ele_match.group(1))
    ele_type = ele_match.group(2)
    ele_shape = ele_match.group(3)
    
    node_ids_str, span = read_option_item(line, ele_shape, Element.get_num_nodes(ele_shape))
    ele_nodes = [ nodes[int(i)-1] for i in node_ids_str]

    if ele_shape == Line2.ShapeName:
        ele = Line2(ele_type, ele_nodes)
    elif ele_shape == Line3.ShapeName:
        ele = Line3(ele_type, ele_nodes)
    elif ele_shape == Tri3.ShapeName:
        ele = Tri3(ele_type, ele_nodes)
    elif ele_shape == Tri6.ShapeName:
        ele = Tri6(ele_type, ele_nodes)
    elif ele_shape == Quad4.ShapeName:
        ele = Quad4(ele_type, ele_nodes)
    elif ele_shape == Tet4.ShapeName:
        ele = Tet4(ele_type, ele_nodes)
    elif ele_shape == Tet10.ShapeName:
        ele = Tet10(ele_type, ele_nodes)
    elif ele_shape == Hex8.ShapeName:
        ele = Hex8(ele_type, ele_nodes)
    else:
        ele = Element(ele_type, ele_shape, ele_nodes)

    ele.id = ele_id
    
    # read fibers
    ele.fibers = Fiber.parse_fibers(line)

    # read remaining options
    # assume only one value per option, which must not be the case in general
    line = line[span[1]:]
    while True:
        line, key = read_next_key(line)
        if line is None:
            break

        num = 1
        if Fiber.get_fiber_type(key) is not None:
            num = 3

        line, value = read_next_value(line, num=num)

        if line is None:
            break
        
        ele.options[key] = value

    return ele