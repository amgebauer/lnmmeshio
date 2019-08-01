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
import re

REGEX_CONDITION = re.compile(r'.*\sCONDITIONS$')

def read_conditions(sections, dat) -> List[ConditionsType]:
    conditions = []
    
    for title, lines in sections.items():

        # Dirichlet conditions
        if title == 'DESIGN POINT DIRICH CONDITIONS':
            conditions.append(PointDirichletConditions.read(lines, dat))
        elif title == 'DESIGN LINE DIRICH CONDITIONS':
            conditions.append(LineDirichletConditions.read(lines, dat))
        elif title == 'DESIGN SURF DIRICH CONDITIONS':
            conditions.append(SurfaceDirichletConditions.read(lines, dat))
        elif title == 'DESIGN VOL DIRICH CONDITIONS':
            conditions.append(VolumeDirichletConditions.read(lines, dat))
        
        # Neumann conditions
        elif title == 'DESIGN POINT NEUMANN CONDITIONS':
            conditions.append(PointNeumannConditions.read(lines, dat))
        elif title == 'DESIGN LINE NEUMANN CONDITIONS':
            conditions.append(LineNeumannConditions.read(lines, dat))
        elif title == 'DESIGN SURF NEUMANN CONDITIONS':
            conditions.append(SurfaceNeumannConditions.read(lines, dat))
        elif title == 'DESIGN VOL NEUMANN CONDITIONS':
            conditions.append(VolumeNeumannConditions.read(lines, dat))
        
        # unknown condition
        elif REGEX_CONDITION.match(title) is not None:
            # check, whether there are non-empty lines
            for line in lines:
                line = line.split('//', 1)[0].strip()
                if line != '':
                    raise NotImplementedError("This type of boundary condition is not yet implemented {0}".format(title))
    return conditions