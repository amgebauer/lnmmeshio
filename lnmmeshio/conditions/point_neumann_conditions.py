from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions

class PointNeumannConditions(CommonConditions):
    
    def __init__(self):
        super(PointNeumannConditions, self).__init__(c.ConditionsType.ActOnType.POINT)
    
    def get_baci_header(self) -> str:
        return "DESIGN POINT NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dis) -> 'PointNeumannConditions':
        return CommonConditions.read(lines, dis, c.ConditionsType.ActOnType.POINT)