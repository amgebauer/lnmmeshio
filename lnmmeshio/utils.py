import numpy as np


def points_on_same_side_of_plane(v1, v2, v3, p1, p2, include_plane=True):
    normal = np.cross(v2 - v1, v3 - v1)
    dotp1 = np.dot(normal, p1 - v1)
    dotp2 = np.dot(normal, p2 - v1)

    if include_plane:
        return np.sign(dotp1) == np.sign(dotp2) or dotp1 == 0.0 or dotp2 == 0.0
    else:
        return np.sign(dotp1) == np.sign(dotp2)
