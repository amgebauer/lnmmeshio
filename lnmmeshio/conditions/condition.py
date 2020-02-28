from collections import OrderedDict
from enum import Enum


class Condition:
    def get_line(self):
        raise NotImplementedError("The condition needs to implement get_line!")


"""
This class is an abstract definition of an condition.
"""


class ConditionsType:
    class ActOnType(Enum):
        POINT = 1
        LINE = 2
        SURFACE = 3
        VOLUME = 4

    def __init__(self, acton: ActOnType):
        self.acton = acton

    def get_baci_header(self):
        raise NotImplementedError(
            "You need to implement the baci header of the condition!"
        )

    def __len__(self):
        raise NotImplementedError("You need to implement the number of conditions!")

    def __getitem__(self, i) -> Condition:
        raise NotImplementedError("You need to implement get!")

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self) -> Condition:
        self.i += 1

        if self.i > len(self):
            raise StopIteration
        return self[self.i - 1]

    def get_sections(self):
        sections = OrderedDict()
        sections[self.get_baci_header()] = []

        if self.acton == ConditionsType.ActOnType.POINT:
            sections[self.get_baci_header()].append("DPOINT {0}".format(len(self)))
        elif self.acton == ConditionsType.ActOnType.LINE:
            sections[self.get_baci_header()].append("DLINE {0}".format(len(self)))
        elif self.acton == ConditionsType.ActOnType.SURFACE:
            sections[self.get_baci_header()].append("DSURF {0}".format(len(self)))
        elif self.acton == ConditionsType.ActOnType.VOLUME:
            sections[self.get_baci_header()].append("DVOL {0}".format(len(self)))

        for item in self:
            sections[self.get_baci_header()].append(item.get_line())

        return sections

    @staticmethod
    def read(lines, dis):
        raise NotImplementedError("This method is not implemented for this class!")
