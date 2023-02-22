from typing import List

from .. import node
from .element import (
    Element,
    Element1D,
    Element2D,
    Element3D,
    ElementHex,
    ElementTet,
    ElementTri,
)
from .parse_element import create_element


def factory(
    shape: str, nodes: List[node.Node], type: str = None, throw_if_unknown: bool = True
) -> Element:
    return create_element(type, shape, nodes, throw_if_unknown=throw_if_unknown)
