from ..ioutils import read_option_item, write_option_list, read_int

class Component:

    def __init__(self, expression, pos):
        self.expression = expression
        self.pos = pos
    
    def write(self, dest):
        d = {
            'COMPONENT': self.pos,
            'FUNCTION': self.expression
        }
        write_option_list(dest, d, newline=True)

    @staticmethod
    def read_component(line):
        pos = read_int(line, 'COMPONENT')

        if pos is None:
            return None
        
        expression = read_option_item(line, 'FUNCTION')[0]
        component = Component(expression, pos)
        
        return component