
from ..ioutils import read_option_item, write_option_list

class BaseVariable:

    def __init__(self, name):
        self.name = name
    
    def write(self, dest):
        d = {
            'VARIABLE': 0,
            'NAME': self.name
        }
        write_option_list(dest, d, newline=False)