from .variable import BaseVariable
from ..ioutils import read_option_item, read_int, read_ints, read_floats, write_option_list

class LinearInterpolationVariable(BaseVariable):
    
    def __init__(self, name: str, times, values):
        super(LinearInterpolationVariable, self).__init__(name)
        self.times = times
        self.values = values
    
    def write(self, dest):
        super(LinearInterpolationVariable, self).write(dest)
        d = {
            'TYPE': 'linearinterpolation',
            'NUMPOINTS': len(self.times),
            'TIMES': self.times,
            'VALUES': self.values
        }
        dest.write(' ')
        write_option_list(dest, d, newline=True)
    
    @staticmethod
    def read_variable(line):
        numpoints = read_int(line, 'NUMPOINTS')
        
        times = read_floats(line, 'TIMES', numpoints)
        values = read_floats(line, 'VALUES', numpoints)

            
        name = read_option_item(line, 'NAME')[0]
        if name is None:
            raise RuntimeError("Expecting NAME of variable to be given. Line is {0}".format(line))

        return LinearInterpolationVariable(name, times, values)



