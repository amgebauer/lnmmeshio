from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions

class SurfaceDirichletConditions(CommonConditions):
    
    def __init__(self):
        super(SurfaceDirichletConditions, self).__init__(c.ConditionsType.ActOnType.SURFACE)
    
    def get_baci_header(self) -> str:
        return "DESIGN SURF DIRICH CONDITIONS"

    @staticmethod
    def read(lines, dis) -> 'SurfaceDirichletConditions':
        return CommonConditions.read(lines, dis, c.ConditionsType.ActOnType.SURFACE)