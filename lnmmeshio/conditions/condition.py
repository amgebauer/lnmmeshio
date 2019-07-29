from enum import Enum
from .. import ioutils

class Condition:

    def write(self, dest):
        raise NotImplementedError("The condition needs to implement write!")

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
        raise NotImplementedError("You need to implement the baci header of the condition!")

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
        return self[self.i-1]

    def write(self, dest):
        ioutils.write_title(dest, self.get_baci_header(), True)
        if self.acton == ConditionsType.ActOnType.POINT:
            dest.write('DPOINT {0}\n'.format(len(self)))
        elif self.acton == ConditionsType.ActOnType.LINE:
            dest.write('DLINE {0}\n'.format(len(self)))
        elif self.acton == ConditionsType.ActOnType.SURFACE:
            dest.write('DSURF {0}\n'.format(len(self)))
        elif self.acton == ConditionsType.ActOnType.VOLUME:
            dest.write('DVOL {0}\n'.format(len(self)))
        
        for item in self:
            item.write(dest)
    
    @staticmethod
    def read(lines, dis):
        raise NotImplementedError("This method is not implemented for this class!")