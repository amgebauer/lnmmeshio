from ..ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from .element import Element
from ..fiber import Fiber
from ..node import Node
from typing import List, Dict
import re
from .parse_element import parse as parse_ele

"""
Class holding all elements in different categories. Current implemented categories are

ElementContainer.structure
ElementContainer.fluid
ElementContainer.ale
ElementContainer.transport
ElementContainer.thermo
"""
class ElementContainer:

    """
    Initialize element contained
    """
    def __init__(self):
        self.structure: List[Element] = None
        self.fluid: List[Element] = None
        self.ale: List[Element] = None
        self.transport: List[Element] = None
        self.thermo: List[Element] = None
    
    """
    Returns the number of structural elements in the discretization

    Returns:
        int: Number of structural parameters in the discretization
    """
    def get_num_structure(self) -> int:
        if self.structure is None:
            return 0
        
        return len(self.structure)

    """
    Returns the number of fluid elements in the discretization

    Returns:
        int: Number of fluid parameters in the discretization
    """
    def get_num_fluid(self) -> int:
        if self.fluid is None:
            return 0
        
        return len(self.fluid)

    """
    Returns the number of ale elements in the discretization

    Returns:
        int: Number of ale parameters in the discretization
    """
    def get_num_ale(self) -> int:
        if self.ale is None:
            return 0
        
        return len(self.ale)

    """
    Returns the number of transport elements in the discretization

    Returns:
        int: Number of transport parameters in the discretization
    """
    def get_num_transport(self) -> int:
        if self.transport is None:
            return 0
        
        return len(self.transport)

    """
    Returns the number of thermo elements in the discretization

    Returns:
        int: Number of thermo parameters in the discretization
    """
    def get_num_thermo(self) -> int:
        if self.thermo is None:
            return 0
        
        return len(self.thermo)

    """
    Write the corresponding sections into the stream like variable dest

    Args:
        dest: Stream like variable, where to write the corresponding sections
    """
    def write(self, dest):
        ElementContainer.__write_section(dest, 'STRUCTURE ELEMENTS', self.structure)
        ElementContainer.__write_section(dest, 'FLUID ELEMENTS', self.fluid)
        ElementContainer.__write_section(dest, 'ALE ELEMENTS', self.ale)
        ElementContainer.__write_section(dest, 'TRANSPORT ELEMENTS', self.transport)
        ElementContainer.__write_section(dest, 'THERMO ELEMENTS', self.thermo)

    """
    Returns a list of List[Elements] for the different element types

    Returns:
        List[List[Element]]
    """
    def values(self):
        ele_list = []

        if self.structure is not None:
            ele_list.append(self.structure)
        if self.fluid is not None:
            ele_list.append(self.fluid)
        if self.ale is not None:
            ele_list.append(self.ale)
        if self.transport is not None:
            ele_list.append(self.transport)
        if self.thermo is not None:
            ele_list.append(self.thermo)

        return ele_list

    """
    Writes the element section with section title and elements. If elements is None,
    the section is not written at all

    Args:
        dest: stream like variable to write
        section_name: string of the section heart
        elements: List of elements
    """
    @staticmethod
    def __write_section(dest, section_name: str, elements: List[Element]):
        if elements is not None:
            write_title(dest, section_name)
            for ele in elements:
                ele.write(dest)

    @staticmethod
    def read_element_sections(sections: Dict[str, List[str]], nodes: List[Node]):
        elec = ElementContainer()
        # read elements
        if 'STRUCTURE ELEMENTS' in sections:
            elec.structure = ElementContainer.__read_elements(nodes, sections['STRUCTURE ELEMENTS'])
        
        if 'FLUID ELEMENTS' in sections:
            elec.fluid = ElementContainer.__read_elements(nodes, sections['FLUID ELEMENTS'])
        
        if 'ALE ELEMENTS' in sections:
            elec.ale = ElementContainer.__read_elements(nodes, sections['ALE ELEMENTS'])
        
        if 'TRANSPORT ELEMENTS' in sections:
            elec.transport = ElementContainer.__read_elements(nodes, sections['TRANSPORT ELEMENTS'])
        
        if 'THERMO ELEMENTS' in sections:
            elec.thermo = ElementContainer.__read_elements(nodes, sections['THERMO ELEMENTS'])
        
        return elec

    """
    Static method that reads the list of elements

    Args:
        nodes: List of nodes (order is important: first node in list must be the one with id 1)
        lines: List of string that represent the lines of the corresponding element section
    
    Returns:
        List of elements
    """
    @staticmethod
    def __read_elements(nodes: List[Node], lines: List[str]):
        eles = []


        for line in lines:

            ele = parse_ele(line, nodes)
            
            if ele is None:
                continue

            eles.append(ele)

            # safety check for integrity of the dat file
            if int(ele.id) != len(eles):
                raise RuntimeError('Element ids in dat file have a gap at {0}!={1}!'.format(ele.id, len(eles)))
            
        
        return eles