from typing import List
from .condition import ConditionsType
from .surf_dirich_condition import SurfaceDirichletConditions
from .point_dirich_condition import PointDirichletConditions
from .line_dirich_conditions import LineDirichletConditions
from .volume_dirich_conditions import VolumeDirichletConditions
from .surf_neumann_condition import SurfaceNeumannConditions
from .point_neumann_conditions import PointNeumannConditions
from .line_neumann_conditions import LineNeumannConditions
from .volume_neumann_conditions import VolumeNeumannConditions

def read_conditions(sections, dat) -> List[ConditionsType]:
    conditions = []
    
    # read dirichlet conditions
    if 'DESIGN POINT DIRICH CONDITIONS' in sections:
        conditions.append(PointDirichletConditions.read(sections['DESIGN POINT DIRICH CONDITIONS'], dat))
    if 'DESIGN LINE DIRICH CONDITIONS' in sections:
        conditions.append(LineDirichletConditions.read(sections['DESIGN LINE DIRICH CONDITIONS'], dat))
    if 'DESIGN SURF DIRICH CONDITIONS' in sections:
        conditions.append(SurfaceDirichletConditions.read(sections['DESIGN SURF DIRICH CONDITIONS'], dat))
    if 'DESIGN VOL DIRICH CONDITIONS' in sections:
        conditions.append(VolumeDirichletConditions.read(sections['DESIGN VOL DIRICH CONDITIONS'], dat))
    
    # read Neumann conditions
    if 'DESIGN POINT NEUMANN CONDITIONS' in sections:
        conditions.append(PointNeumannConditions.read(sections['DESIGN POINT NEUMANN CONDITIONS'], dat))
    if 'DESIGN LINE NEUMANN CONDITIONS' in sections:
        conditions.append(LineNeumannConditions.read(sections['DESIGN LINE NEUMANN CONDITIONS'], dat))
    if 'DESIGN SURF NEUMANN CONDITIONS' in sections:
        conditions.append(SurfaceNeumannConditions.read(sections['DESIGN SURF NEUMANN CONDITIONS'], dat))
    if 'DESIGN VOL NEUMANN CONDITIONS' in sections:
        conditions.append(VolumeNeumannConditions.read(sections['DESIGN VOL NEUMANN CONDITIONS'], dat))

    return conditions