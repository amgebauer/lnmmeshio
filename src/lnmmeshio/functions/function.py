from collections import OrderedDict

from ..ioutils import read_option_item, write_title
from .component import Component
from .variable import BaseVariable
from .variablereader import read_variable


class Function:
    def __init__(self, id):
        self.id = id
        self.components = []
        self.variables = {}

    def reset(self):
        self.id = None

    def add_component(self, component: Component):
        if component.pos < len(self.components):
            raise RuntimeError("This component is already added to the function")
        elif component.pos > len(self.components):
            raise RuntimeError(
                "There is at least one component missing. Got component {0} but expected {1}".format(
                    component.pos, len(self.components)
                )
            )

        self.components.append(component)

    def add_variable(self, variable: BaseVariable):
        if variable.name in self.variables:
            raise RuntimeError("The variable with the same name already exists")

        self.variables[variable.name] = variable

    def get_sections(self):
        d = OrderedDict()

        lines = []

        for c in self.components:
            lines.append(c.get_line())

        for v in self.variables.values():
            lines.append(v.get_line())
        d["FUNCT{0}".format(self.id)] = lines

        return d

    def write(self, dest):
        write_title(dest, "FUNCT{0}".format(self.id), True)

        for c in self.components:
            c.write(dest)

        for v in self.variables.values():
            v.write(dest)

    @staticmethod
    def read_functions(sections):
        # read functions
        maxf = 10

        functions = []
        for i in range(maxf):
            if "FUNCT{0}".format(i) in sections:
                # function exists
                # parse function

                curr_function = None
                # read each component
                for line in sections["FUNCT{0}".format(i)]:
                    component = None
                    variable = None
                    if read_option_item(line, "COMPONENT")[0] is not None:
                        # this is a component
                        component = Component.read_component(line)
                    elif read_option_item(line, "VARIABLE")[0] is not None:
                        # this is a variable
                        variable = read_variable(line)

                    if component is not None:
                        # add to function
                        if curr_function is None:
                            curr_function = Function(i)
                            if i - 1 != len(functions):
                                raise RuntimeError(
                                    "The functions are not in the correct order"
                                )

                        curr_function.add_component(component)

                    if variable is not None:
                        curr_function.add_variable(variable)

                if curr_function is not None:
                    functions.append(curr_function)

        return functions
