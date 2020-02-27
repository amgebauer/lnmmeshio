from enum import Enum
import io
from .element.element import Element
from .node import Node
from .ioutils import read_option_item, read_float, read_int


class ResultDescription:
    def __init__(self, item, quantity: str, value: float, tolerance: float):
        self.item = item
        self.quantity = quantity
        self.value = value
        self.tolerance = tolerance

    def get_line(self):
        l = io.StringIO()

        if isinstance(self.item, Element):
            l.write("ELEMENT {0}".format(self.item.id))
        elif isinstance(self.item, Node):
            l.write("NODE {0}".format(self.item.id))
        else:
            ValueError("Unknown item to act on: {0}".format(type(self.item)))

        l.write(
            " QUANTITY {0} VALUE {1} TOLERANCE {2}".format(
                self.quantity, self.value, self.tolerance
            )
        )
        return l.getvalue()

    @staticmethod
    def parseall(sections, datfile):
        if "RESULT DESCRIPTION" not in sections:
            return []

        r = []
        for line in sections["RESULT DESCRIPTION"]:
            d = ResultDescription.parse(line, datfile)

            if d is not None:
                r.append(d)

        return r

    @staticmethod
    def parse(line, datfile):
        # strip comments
        line = line.split("//")[0].strip()

        if line == "":
            return None

        quantity = read_option_item(line, "QUANTITY", 1)[0]
        value = read_float(line, "VALUE")
        tolerance = read_float(line, "TOLERANCE")

        item = None
        try:
            nodeid = read_int(line, "NODE")
            item = datfile.discretization.nodes[nodeid - 1]
        except RuntimeError:
            pass

        dis = read_option_item(line, "DIS", 1)[0]
        if dis == "structure":
            if item is None:
                try:
                    elementid = read_int(line, "ELEMENT")
                    item = datfile.discretization.elements.structure[elementid - 1]
                except RuntimeError:
                    raise ValueError(
                        "Unknown node or element of result description: {0}".format(
                            line
                        )
                    )
            return StructureResultDescription(item, quantity, value, tolerance)
        else:
            raise ValueError("Unknown result description: {0}".format(line))

        return None


class StructureResultDescription(ResultDescription):
    def __init__(self, item, quantity, value, tolerance):
        super(StructureResultDescription, self).__init__(
            item, quantity, value, tolerance
        )

    def get_line(self):
        return "STRUCTURE DIS structure {0}".format(
            super(StructureResultDescription, self).get_line()
        )
