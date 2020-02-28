
from . import condition as c
from .common_condition import CommonConditions


class SurfaceNeumannConditions(CommonConditions):
    def __init__(self):
        super(SurfaceNeumannConditions, self).__init__(
            c.ConditionsType.ActOnType.SURFACE
        )

    def get_baci_header(self) -> str:
        return "DESIGN SURF NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "SurfaceNeumannConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.SURFACE)
