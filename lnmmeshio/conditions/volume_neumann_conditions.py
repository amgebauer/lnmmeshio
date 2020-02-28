
from . import condition as c
from .common_condition import CommonConditions


class VolumeNeumannConditions(CommonConditions):
    def __init__(self):
        super(VolumeNeumannConditions, self).__init__(c.ConditionsType.ActOnType.VOLUME)

    def get_baci_header(self) -> str:
        return "DESIGN VOL NEUMANN CONDITIONS"

    @staticmethod
    def read(lines, dat) -> "VolumeNeumannConditions":
        return CommonConditions.read(lines, dat, c.ConditionsType.ActOnType.VOLUME)
