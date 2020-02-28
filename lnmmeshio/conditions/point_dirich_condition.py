from . import condition as c
from .common_condition import CommonConditions


class PointDirichletConditions(CommonConditions):
    def __init__(self):
        super(PointDirichletConditions, self).__init__(c.ConditionsType.ActOnType.POINT)

    def get_baci_header(self) -> str:
        return "DESIGN POINT DIRICH CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "PointDirichletConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.POINT)
