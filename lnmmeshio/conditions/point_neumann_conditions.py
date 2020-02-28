
from . import condition as c
from .common_condition import CommonConditions


class PointNeumannConditions(CommonConditions):
    def __init__(self):
        super(PointNeumannConditions, self).__init__(c.ConditionsType.ActOnType.POINT)

    def get_baci_header(self) -> str:
        return "DESIGN POINT NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "PointNeumannConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.POINT)
