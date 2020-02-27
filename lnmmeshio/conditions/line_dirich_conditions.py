from . import condition as c
from ..ioutils import read_option_item
import numpy as np
from .common_condition import CommonCondition, CommonConditions


class LineDirichletConditions(CommonConditions):
    def __init__(self):
        super(LineDirichletConditions, self).__init__(c.ConditionsType.ActOnType.LINE)

    def get_baci_header(self) -> str:
        return "DESIGN LINE DIRICH CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "LineDirichletConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.LINE)
