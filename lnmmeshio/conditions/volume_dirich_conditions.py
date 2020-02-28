
from . import condition as c
from .common_condition import CommonConditions


class VolumeDirichletConditions(CommonConditions):
    def __init__(self):
        super(VolumeDirichletConditions, self).__init__(
            c.ConditionsType.ActOnType.VOLUME
        )

    def get_baci_header(self) -> str:
        return "DESIGN VOL DIRICH CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "VolumeDirichletConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.VOLUME)
