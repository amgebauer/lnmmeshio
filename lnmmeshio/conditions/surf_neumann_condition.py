from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions

class SurfaceNeumannConditions(CommonConditions):
    
    def __init__(self):
        super(SurfaceNeumannConditions, self).__init__(c.ConditionsType.ActOnType.SURFACE)
    
    def get_baci_header(self) -> str:
        return "DESIGN SURF NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dis) -> 'SurfaceNeumannConditions':
        return CommonConditions.read(lines, dis, c.ConditionsType.ActOnType.SURFACE)