from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions

class VolumeNeumannConditions(CommonConditions):
    
    def __init__(self):
        super(VolumeNeumannConditions, self).__init__(c.ConditionsType.ActOnType.VOLUME)
    
    def get_baci_header(self) -> str:
        return "DESIGN VOL NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dis) -> 'VolumeNeumannConditions':
        return CommonConditions.read(lines, dis, c.ConditionsType.ActOnType.VOLUME)