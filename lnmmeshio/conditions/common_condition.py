from . import condition as c
from ..ioutils import read_option_item
import numpy as np

class CommonCondition(c.Condition):
    
    def __init__(self, nodeset, onoff, value, acton: c.ConditionsType.ActOnType, funct=None):
        self.onoff = onoff
        self.nodeset = nodeset
        self.value = value
        self.funct = funct
        self.acton = acton

    def get_line(self):
        if self.funct is None:
            fcns = [0]
        else:
            fcns = [f.id for f in self.funct]
        
        if len(fcns) == 1:
            fcns *= len(self.onoff)
        
        if len(fcns) != len(self.onoff) or len(self.onoff) != len(self.value):
            raise RuntimeError("Dimensions do not fit!")

        return "E {0} - NUMDOF {1} ONOFF {2} VAL {3} FUNCT {4}".format(
            self.nodeset.id, len(self.onoff),
            ' '.join(['1' if i==True else '0' for i in self.onoff]),
            ' '.join([str(i) for i in self.value]),
            ' '.join([str(i) for i in fcns])
        )

    @staticmethod
    def read(line, dat, acton):
        nodeset_id_str = read_option_item(line, 'E')[0]
        if nodeset_id_str is None:
            return None
        numdof = int(read_option_item(line, 'NUMDOF', 1)[0])
        onoff_str = read_option_item(line, 'ONOFF', numdof)[0]
        value = read_option_item(line, 'VAL', numdof)[0]
        fcn = read_option_item(line, 'FUNCT', numdof)[0]

        if acton == c.ConditionsType.ActOnType.POINT:
            nodeset = dat.discretization.pointnodesets[int(nodeset_id_str)-1]
        elif acton == c.ConditionsType.ActOnType.LINE:
            nodeset = dat.discretization.linenodesets[int(nodeset_id_str)-1]
        elif acton == c.ConditionsType.ActOnType.SURFACE:
            nodeset = dat.discretization.surfacenodesets[int(nodeset_id_str)-1]
        elif acton == c.ConditionsType.ActOnType.VOLUME:
            nodeset = dat.discretization.volumenodesets[int(nodeset_id_str)-1]
        onoff = np.array([int(i) for i in onoff_str], dtype=bool)
        value = np.array(value, dtype=float)
        fcn = np.array(fcn, dtype=int)

        if np.any(fcn):
            fcns = [None]*numdof
            for i, f in enumerate(fcn):
                if f > 0:
                    fcns[i] = dat.functions[f-1]

        return CommonCondition(nodeset, onoff, value, acton)


class CommonConditions(c.ConditionsType):
    
    def __init__(self, acton: c.ConditionsType.ActOnType):
        super(CommonConditions, self).__init__(acton)
        self.conditions = []

    
    def __len__(self) -> int:
        return len(self.conditions)
    
    def __getitem__(self, i) -> CommonCondition:
        return self.conditions[i]
    
    def add(self, cond):
        self.conditions.append(cond)

    @staticmethod
    def read(lines, dis, acton: c.ConditionsType.ActOnType) -> 'CommonConditions':
        conditions = CommonConditions(acton)
        number = None
        for line in lines:

            line = line.split('//', 1)[0].strip()
            if line == '':
                continue

            if number is None:
                if conditions.acton == c.ConditionsType.ActOnType.POINT:
                    number = int(read_option_item(line, 'DPOINT')[0])
                elif conditions.acton == c.ConditionsType.ActOnType.LINE:
                    number = int(read_option_item(line, 'DLINE')[0])
                elif conditions.acton == c.ConditionsType.ActOnType.SURFACE:
                    number = int(read_option_item(line, 'DSURF')[0])
                elif conditions.acton == c.ConditionsType.ActOnType.VOLUME:
                    number = int(read_option_item(line, 'DVOL')[0])
            else:
                cond = CommonCondition.read(line, dis, acton)
                if cond is not None:
                    conditions.add(cond)
        
        if number != len(conditions):
            print('Found {0} bcs but expected {1}'.format(len(conditions), number))
        
        return conditions

