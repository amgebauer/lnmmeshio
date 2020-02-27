from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions


class LineNeumannConditions(CommonConditions):
    def __init__(self):
        super(LineNeumannConditions, self).__init__(c.ConditionsType.ActOnType.LINE)

    def get_baci_header(self) -> str:
        return "DESIGN LINE NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "LineNeumannConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.LINE)
