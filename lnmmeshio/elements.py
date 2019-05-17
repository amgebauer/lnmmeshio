#
# Maintainer: Amadeus Gebauer
#

import numpy as np
from numpy  import array,zeros, cross
from math   import sqrt

from progress.bar import Bar

def da(r,c):
    return zeros((r,c))

elementtypes = {
                "TET4"    : 4,
                "TET10"   : 10,
                "PYRAMID5": 5,
                "HEX8"    : 8,
                "HEX20"   : 20,
                "HEX27"   : 27,
                "WEDGE6"  : 6,
                "QUAD4"   : 4,
                "TRI3"    : 3,
                "LINE2"   : 2,
                "QUAD9"   : 9,
                }

surfaces = {
            "TET4": [[0, 1, 3],
                     [1, 2, 3],
                     [0, 3, 2],
                     [0, 2, 1]],
            "TET10":[[0, 1, 3, 4, 8, 7],
                     [1, 2, 3, 5, 9, 8],
                     [0, 3, 2, 7, 9, 6],
                     [0, 2, 1, 6, 5, 4]],
            "PYRAMID5": [[0, 3, 2, 1],
                         [0,1,4],
                         [1,2,4],
                         [2,3,4],
                         [0,4,3]],
            "HEX8": [[0,  3,  2,  1],
                     [0,  1,  5,  4],
                     [1,  2,  6,  5],
                     [2,  3,  7,  6],
                     [0,  4,  7,  3],
                     [4,  5,  6,  7]],
            "HEX20": [[0,  3,  2,  1],
                     [0,  1,  5,  4],
                     [1,  2,  6,  5],
                     [2,  3,  7,  6],
                     [0,  4,  7,  3],
                     [4,  5,  6,  7]],
            "HEX27": [[0,  3,  2,  1],
                     [0,  1,  5,  4],
                     [1,  2,  6,  5],
                     [2,  3,  7,  6],
                     [0,  4,  7,  3],
                     [4,  5,  6,  7]],
            "WEDGE6": [[0, 1, 2],
                       [3, 4, 5],
                       [0, 1, 4, 3],
                       [1, 2, 5, 4],
                       [0, 3, 5, 2]],
            "QUAD4": [[0,1,2,3]],
            "QUAD9": [[0,1,2,3]],
            "TRI3": [[0,1,2]],
            "LINE2": [[0,1]],
            }

elementlines = {
               'QUAD4': [[0,1],[1,2],[2,3],[3,0]],
               'QUAD9': [[0,1],[1,2],[2,3],[3,0]]
               }

ensight2baci = {
                "tetra4"        : "TET4",
                "tetra10"       : "TET10",
                "pyramid5"      : "PYRAMID5",
                "hexa8"         : "HEX8",
                "hexa20"        : "HEX20",
                "hexa27"        : "HEX27",
                "penta6"        : "WEDGE6",
                "quad9"         : "QUAD9",
                "quad8"         : "QUAD8",
                "quad4"         : "QUAD4",
                "tria6"         : "TRI6",
                "tria3"         : "TRI3",
                "bar2"          : "LINE2",
                }

class Element( object ):

    def __init__( self, nodes, matID ):
        self._nodes = nodes
        self._matID = matID

    def name(self):
        raise "Subclass should reimplement this function"

    def nodes(self):
        return self._nodes

    def matID(self):
        return self._matID

    def checkjacobi(self,nodemap):
        # complain by default
        print("default in element type {0}".format(self.name()))
        return 1

    def check2d(self,nodemap):
        for r in [-0.5,0.5]:
            for s in [-0.5,0.5]:
                deriv = self.deriv(r,s)
                xjm = da(2,2)
                for i,n in enumerate(self.nodes()):
                    n = nodemap[n]
                    xjm[0,0] += deriv[0,i]*n[0]
                    xjm[1,0] += deriv[1,i]*n[0]
                    xjm[0,1] += deriv[0,i]*n[1]
                    xjm[1,1] += deriv[1,i]*n[1]
                det = xjm[0,0]*xjm[1,1] - xjm[1,0]*xjm[0,1]
                if det <= 0.:
                    #return det
                    return 1
        return 0

    def check3d(self,nodemap):
        for i in range(self.qxg.shape[0]):
            r,s,t = self.qxg[i,0],self.qxg[i,1],self.qxg[i,2]
            deriv = self.deriv(r,s,t)
            xjm = da(3,3)
            for i,n in enumerate(self.nodes()):
                n = nodemap[n]
                xjm[0,0] += deriv[0,i]*n[0]
                xjm[1,0] += deriv[1,i]*n[0]
                xjm[2,0] += deriv[2,i]*n[0]
                xjm[0,1] += deriv[0,i]*n[1]
                xjm[1,1] += deriv[1,i]*n[1]
                xjm[2,1] += deriv[2,i]*n[1]
                xjm[0,2] += deriv[0,i]*n[2]
                xjm[1,2] += deriv[1,i]*n[2]
                xjm[2,2] += deriv[2,i]*n[2]
            det = (xjm[0,0]*xjm[1,1]*xjm[2,2]+
                   xjm[0,1]*xjm[1,2]*xjm[2,0]+
                   xjm[0,2]*xjm[1,0]*xjm[2,1]-
                   xjm[0,2]*xjm[1,1]*xjm[2,0]-
                   xjm[0,0]*xjm[1,2]*xjm[2,1]-
                   xjm[0,1]*xjm[1,0]*xjm[2,2])
            if det <= 0.:
                return 1
        return 0

    def checkrewind(self,nodemap):
        if self.check3d(nodemap):
            nodes = [self._nodes[self.rewind[i]] for i in range(len(self._nodes))]
            self._nodes = nodes
            # paranoia test
            if self.check3d(nodemap):
                for n in self._nodes:
                    print(n)
                raise Exception("rewind failed for %s element" % (self.name(),))
            return True
        return False

    def surfaces(self):
        work_nodes    = self.nodes()
        surfaces_local = surfaces[ensight2baci[self.name()]]
        surfaces_global = [ [work_nodes[ws] for ws in worksurf] for worksurf in surfaces_local ]

        return surfaces_global

    def volume(self):
        raise 'Subclass has to implement this'

    def barycenter(self,nodemap):
        work_nodes    = self.nodes()
        l             = len(work_nodes)
        barycenter    = [sum([ nodemap[work_nodes[i]][j] for i in range(l)])/l for j in [0,1,2]]
        return barycenter

class Line2Element( Element ):

    def name(self):
        return "bar2"

    def LineElementLength(self, nodemap):
        cur_nodeids = self.nodes()
        cur_nodes   = [ nodemap[ni] for ni in cur_nodeids ]
        return np.linalg.norm( [cur_nodes[0][i] - cur_nodes[1][i] for i in [0,1,2]] )


class Tri3Element( Element ):

    def name(self):
        return "tria3"

    rewind = [0,2,1]

    def deriv(self,r,s):
        deriv = da(2,3)
        deriv[0, 0]=-1.0
        deriv[1, 0]=-1.0
        deriv[0, 1]= 1.0
        deriv[1, 1]= 0.0
        deriv[0, 2]= 0.0
        deriv[1, 2]= 1.0
        return deriv

    def checkjacobi(self,nodemap):
        return self.check2d(nodemap)

    def checkrewind(self,nodemap):
        if self.check2d(nodemap):
            nodes = [self._nodes[self.rewind[i]] for i in range(len(self._nodes))]
            self._nodes = nodes
            # paranoia test
            if self.check2d(nodemap):
                for n in self._nodes:
                    print(n)
                raise Exception("rewind failed for %s element" % (self.name(),))
            return True
        return False

class Tri6Element( Element ):

    def name(self):
        return "tria6"

class Tet4Element( Element ):

    palpha = (5.0 + 3.0*sqrt(5.0))/20.0
    pbeta  = (5.0 - sqrt(5.0))/20.0
    qxg = array([[pbeta , pbeta , pbeta ,],
                 [palpha, pbeta , pbeta ,],
                 [pbeta , palpha, pbeta ,],
                 [pbeta , pbeta , palpha,]])
    rewind = [0,2,1,3]

    def name(self):
        return "tetra4"

    def deriv(self,r,s,t):
        deriv = da(3,4)
        deriv[0, 0]=-1.0
        deriv[0, 1]= 1.0
        deriv[0, 2]= 0.0
        deriv[0, 3]= 0.0

        deriv[1, 0]=-1.0
        deriv[1, 1]= 0.0
        deriv[1, 2]= 1.0
        deriv[1, 3]= 0.0

        deriv[2, 0]=-1.0
        deriv[2, 1]= 0.0
        deriv[2, 2]= 0.0
        deriv[2, 3]= 1.0
        return deriv

    def checkjacobi(self,nodemap):
        return self.check3d(nodemap)

    def gnuplot(self,f,nodemap):
        n = [nodemap[n] for n in self.nodes()]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,"\n"
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,"\n"
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,"\n"
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,"\n"

    def volume(self, nodemap):
        nodes = self.nodes()

        N0 = nodemap[nodes[0]]
        N1 = nodemap[nodes[1]]
        N2 = nodemap[nodes[2]]
        N3 = nodemap[nodes[3]]

        a = [ N1[i] - N0[i] for i in [0,1,2]]
        b = [ N2[i] - N0[i] for i in [0,1,2]]
        c = [ N3[i] - N0[i] for i in [0,1,2]]

        V = abs(np.dot(cross(a,b),c))/6.0
        return V

class Tet10Element( Element ):

    palpha = (5.0 + 3.0*sqrt(5.0))/20.0
    pbeta  = (5.0 - sqrt(5.0))/20.0
    qxg = array([[pbeta , pbeta , pbeta ,],
                 [palpha, pbeta , pbeta ,],
                 [pbeta , palpha, pbeta ,],
                 [pbeta , pbeta , palpha,]])
    rewind = [0,2,1,3,6,5,4,7,8,9]

    def name(self):
        return "tetra10"

    def deriv(self,r,s,t):
        u=1.0-r-s-t
        deriv = da(3,10)
        deriv[0, 0] = -4*u+1
        deriv[1, 0] = deriv[0, 0]
        deriv[2, 0] = deriv[0, 0]

        deriv[0, 1] = 4*r-1
        deriv[1, 1] = 0
        deriv[2, 1] = 0

        deriv[0, 2] = 0
        deriv[1, 2] = 4*s-1
        deriv[2, 2] = 0

        deriv[0, 3] = 0
        deriv[1, 3] = 0
        deriv[2, 3] = 4*t-1

        deriv[0, 4] = 4*(u-r)
        deriv[1, 4] = -4*r
        deriv[2, 4] = -4*r

        deriv[0, 5] = 4*s
        deriv[1, 5] = 4*r
        deriv[2, 5] = 0

        deriv[0, 6] = -4*s
        deriv[1, 6] = 4*(u-s)
        deriv[2, 6] = -4*s

        deriv[0, 7] = -4*t
        deriv[1, 7] = -4*t
        deriv[2, 7] = 4*(u-t)

        deriv[0, 8] = 4*t
        deriv[1, 8] = 0
        deriv[2, 8] = 4*r

        deriv[0, 9] = 0
        deriv[1, 9] = 4*t
        deriv[2, 9] = 4*s
        return deriv

    def checkjacobi(self,nodemap):
        return self.check3d(nodemap)

    def volume(self, nodemap):

        nodes = self.nodes()
        N0 = nodemap[nodes[0]]
        N1 = nodemap[nodes[1]]
        N2 = nodemap[nodes[2]]
        N3 = nodemap[nodes[3]]

        a = [ N1[i] - N0[i] for i in [0,1,2]]
        b = [ N2[i] - N0[i] for i in [0,1,2]]
        c = [ N3[i] - N0[i] for i in [0,1,2]]

        V = abs(np.dot(cross(a,b),c))/6.0
        return V

class Quad4Element( Element ):

    def name(self):
        return "quad4"

    def deriv(self,r,s):
        rp=1.0+r
        rm=1.0-r
        sp=1.0+s
        sm=1.0-s
        deriv = da(2,4)
        deriv[0, 0]=-0.25*sm
        deriv[1, 0]=-0.25*rm
        deriv[0, 1]= 0.25*sm
        deriv[1, 1]=-0.25*rp
        deriv[0, 2]= 0.25*sp
        deriv[1, 2]= 0.25*rp
        deriv[0, 3]=-0.25*sp
        deriv[1, 3]= 0.25*rm
        return deriv

    def checkjacobi(self,nodemap):
        return self.check2d(nodemap)


class Quad8Element( Element ):

    def name(self):
        return "quad8"

class Quad9Element( Element ):

    def name(self):
        return "quad9"

class Hex8Element( Element ):

    xi2 = 0.5773502691896
    qxg = array([
        [-xi2, -xi2, -xi2,],
        [ xi2, -xi2, -xi2,],
        [ xi2,  xi2, -xi2,],
        [-xi2,  xi2, -xi2,],
        [-xi2, -xi2,  xi2,],
        [ xi2, -xi2,  xi2,],
        [ xi2,  xi2,  xi2,],
        [-xi2,  xi2,  xi2,],
        ])
    rewind = [4,5,6,7,0,1,2,3]

    def name(self):
        return "hexa8"

    def surfaces(self):
        return [[self._nodes[0],self._nodes[3],self._nodes[2],self._nodes[1]],
                [self._nodes[0],self._nodes[1],self._nodes[5],self._nodes[4]],
                [self._nodes[1],self._nodes[2],self._nodes[6],self._nodes[5]],
                [self._nodes[2],self._nodes[3],self._nodes[7],self._nodes[6]],
                [self._nodes[0],self._nodes[4],self._nodes[7],self._nodes[3]],
                [self._nodes[4],self._nodes[5],self._nodes[6],self._nodes[7]]]

    def deriv(self,r,s,t):
        deriv = da(3,8)

        rp=1.0+r
        rm=1.0-r
        sp=1.0+s
        sm=1.0-s
        tp=1.0+t
        tm=1.0-t

        deriv[0, 0]=-.125*sm*tm
        deriv[1, 0]=-.125*tm*rm
        deriv[2, 0]=-.125*rm*sm

        deriv[0, 1]= .125*sm*tm
        deriv[1, 1]=-.125*tm*rp
        deriv[2, 1]=-.125*rp*sm

        deriv[0, 2]= .125*sp*tm
        deriv[1, 2]= .125*tm*rp
        deriv[2, 2]=-.125*rp*sp

        deriv[0, 3]=-.125*sp*tm
        deriv[1, 3]= .125*tm*rm
        deriv[2, 3]=-.125*rm*sp

        deriv[0, 4]=-.125*sm*tp
        deriv[1, 4]=-.125*tp*rm
        deriv[2, 4]= .125*rm*sm

        deriv[0, 5]= .125*sm*tp
        deriv[1, 5]=-.125*tp*rp
        deriv[2, 5]= .125*rp*sm

        deriv[0, 6]= .125*sp*tp
        deriv[1, 6]= .125*tp*rp
        deriv[2, 6]= .125*rp*sp

        deriv[0, 7]=-.125*sp*tp
        deriv[1, 7]= .125*tp*rm
        deriv[2, 7]= .125*rm*sp

        return deriv

    def checkjacobi(self,nodemap):
        return self.check3d(nodemap)

    def gnuplot(self,f,nodemap):
        n = [nodemap[n] for n in self.nodes()]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,"\n"
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,n[5][0],n[5][1],n[5][2]
        print >>f,n[6][0],n[6][1],n[6][2]
        print >>f,n[7][0],n[7][1],n[7][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[5][0],n[5][1],n[5][2]
        print >>f,"\n"
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[6][0],n[6][1],n[6][2]
        print >>f,"\n"
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,n[7][0],n[7][1],n[7][2]
        print >>f,"\n"

class Hex20Element( Element ):

    def name(self):
        return "hexa20"

    # Reordering of nodes neccessary since Ensight Gold format for HEX20 elements differs from Baci format
    def nodes(self):
        return self._nodes[:12]+self._nodes[16:20]+self._nodes[12:16]


class Wedge6Element( Element ):

    xi3 = 1.0/sqrt(3.0)
    qxg = array([[2./3., 1./6., xi3, ],
                 [1./6., 2./3., xi3, ],
                 [1./6., 1./6., xi3, ],
                 [2./3., 1./6., -xi3,],
                 [1./6., 2./3., -xi3,],
                 [1./6., 1./6., -xi3,]])
    rewind = [3,4,5,0,1,2]

    def name(self):
        return "penta6"

    def deriv(self,r,s,t):
        deriv = da(3,6)

        p1=.5*(1-t)
        p2=.5*(1+t)
        t3=1.0-r-s

        deriv[0, 0]=p1
        deriv[0, 1]=0
        deriv[0, 2]=-p1
        deriv[0, 3]=p2
        deriv[0, 4]=0
        deriv[0, 5]=-p2

        deriv[1, 0]=0
        deriv[1, 1]=p1
        deriv[1, 2]=-p1
        deriv[1, 3]=0
        deriv[1, 4]=p2
        deriv[1, 5]=-p2

        deriv[2, 0]=-.5*r
        deriv[2, 1]=-.5*s
        deriv[2, 2]=-.5*t3
        deriv[2, 3]=.5*r
        deriv[2, 4]=.5*s
        deriv[2, 5]=.5*t3

        return deriv

    def checkjacobi(self,nodemap):
        return self.check3d(nodemap)

class Wedge15Element( Element ):

    def name(self):
        return "penta15"


class Pyramid5Element( Element ):

    qxg = array([[-0.26318405556971, -0.26318405556971, 0.54415184401122,],
                 [-0.50661630334979, -0.50661630334979, 0.12251482265544,],
                 [-0.26318405556971,  0.26318405556971, 0.54415184401122,],
                 [-0.50661630334979,  0.50661630334979, 0.12251482265544,],
                 [ 0.26318405556971, -0.26318405556971, 0.54415184401122,],
                 [ 0.50661630334979, -0.50661630334979, 0.12251482265544,],
                 [ 0.26318405556971,  0.26318405556971, 0.54415184401122,],
                 [ 0.50661630334979,  0.50661630334979, 0.12251482265544,]])
    rewind = [0,3,2,1,4]
    #rewind = [1,0,3,2,4]

    def name(self):
        return "pyramid5"

    def deriv(self,r,s,t):
        deriv = da(3,5)

        rationdr=s*t/(1-t)
        rationds=r*t/(1-t)
        rationdt=r*s*(1-2.0*t)/((1-t)*(1-t))

        deriv[0,0]=.25*(-1+rationdr);
        deriv[0,1]=.25*(1-rationdr);
        deriv[0,2]=.25*(1+rationdr);
        deriv[0,3]=.25*(-1-rationdr);
        deriv[0,4]=0;

        deriv[1,0]=.25*(-1+rationds);
        deriv[1,1]=.25*(-1-rationds);
        deriv[1,2]=.25*(1+rationds);
        deriv[1,3]=.25*(1-rationds);
        deriv[1,4]=0;

        deriv[2,0]=.25*(rationdt-1);
        deriv[2,1]=.25*(-1*rationdt-1);
        deriv[2,2]=.25*(rationdt-1);
        deriv[2,3]=.25*(-1*rationdt-1);
        deriv[2,4]=1;

        return deriv

    def gnuplot(self,f,nodemap):
        n = [nodemap[n] for n in self.nodes()]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,"\n"
        print >>f,n[0][0],n[0][1],n[0][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"
        print >>f,n[1][0],n[1][1],n[1][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"
        print >>f,n[2][0],n[2][1],n[2][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"
        print >>f,n[3][0],n[3][1],n[3][2]
        print >>f,n[4][0],n[4][1],n[4][2]
        print >>f,"\n"

    def checkjacobi(self,nodemap):
        return self.check3d(nodemap)


class Pyramid13Element( Element ):

    def name(self):
        return "pyramid13"

class Hex18Element( Element ):

    def name(self):
        return "hexa18"


def readelement(line):
    # since ensight gold standard doesn't support HEX27 elements only the HEX20 nodes are regarded
    if line[2]=="HEX27":     return Hex20Element(    [int(line[i]) for i in range(3,23)], int(line[24]) )
    if line[2]=="NURBS27":   return Hex20Element(    [int(line[i]) for i in [3,5,11,9,21,23,29,27,4,8,10,6,12,14,20,18,22,26,28,24]], int(line[31]) )
    if line[2]=="NURBS9":    return Quad9Element(    [int(line[i]) for i in range(3,12)], int(line[13]) )
    if line[2]=="HEX20":     return Hex20Element(    [int(line[i]) for i in range(3,23)], int(line[24]) )
    if line[2]=="HEX8":      return Hex8Element(     [int(line[i]) for i in range(3,11)], int(line[12]) )
    if line[2]=="PYRAMID13": return Pyramid13Element([int(line[i]) for i in range(3,16)], int(line[17]) )
    if line[2]=="PYRAMID5":  return Pyramid5Element( [int(line[i]) for i in range(3, 8)], int(line[9]) )
    if line[2]=="QUAD4":     return Quad4Element(    [int(line[i]) for i in range(3, 7)], int(line[8]) )
    if line[2]=="QUAD8":     return Quad8Element(    [int(line[i]) for i in range(3,11)], int(line[12]) )
    if line[2]=="QUAD9":     return Quad9Element(    [int(line[i]) for i in range(3,12)], int(line[13]) )
    if line[2]=="TET10":     return Tet10Element(    [int(line[i]) for i in range(3,13)], int(line[14]) )
    if line[2]=="TET4":      return Tet4Element(     [int(line[i]) for i in range(3, 7)], int(line[8]) )
    if line[2]=="TRI3":      return Tri3Element(     [int(line[i]) for i in range(3, 6)], int(line[7]) )
    if line[2]=="TRI6":      return Tri6Element(     [int(line[i]) for i in range(3, 9)], int(line[10]) )
    if line[2]=="WEDGE15":   return Wedge15Element(  [int(line[i]) for i in range(3,18)], int(line[19]) )
    if line[2]=="WEDGE6":    return Wedge6Element(   [int(line[i]) for i in range(3, 9)], int(line[10]) )
    if line[2]=="LINE2":     return Line2Element(    [int(line[i]) for i in range(3, 5)], int(line[6]) )
    if line[2]=="HEX18":     return Hex18Element(    [int(line[i]) for i in range(3, 21)], int(line[22]) )
    raise Exception("unsupported element type '%s'" % line[2])


def readnodes(sections):
    nodes = []
    nodeids = []
    fiber1 = []
    fiber2 = []
    nodemap = {}
    for line in Bar('read nodes').iter(sections["NODE COORDS"]):
        nid = int(line[1])
        node = (float(line[3]),float(line[4]),float(line[5]))
        nodes.append(node)
        nodeids.append(nid)
        nodemap[nid] = node
        if 'FIBER1' in line:
            fiber1.append((float(line[7]),float(line[8]),float(line[9])))
        if 'FIBER2' in line:
            fiber2.append((float(line[11]),float(line[12]),float(line[13])))
    if fiber1:
        assert len(fiber1)==len(nodes)
    if fiber2:
        assert len(fiber2)==len(nodes)
    return nodes, nodeids, nodemap, fiber1, fiber2


def surfacemesh(section):
    volumeelements = {}

    for e in Bar('read elements').iter(section):
        assert e[2] in elementtypes

        nodes = [int(i) for i in e[3:3+elementtypes[e[2]]]]
        surfs = surfaces[e[2]]

        for surf in surfs:
            localnodes = set()
            for n in surf:
                localnodes.add(nodes[n])
            localnodes = tuple(sorted(localnodes))
            if localnodes not in volumeelements:
                volumeelements[localnodes] = []
            volumeelements[localnodes].append(int(e[0]))

    mesh = {}
    for localnodes in Bar('extract surface').iter(volumeelements):
        eids = volumeelements[localnodes]
        if len(eids)==1:
            mesh[eids[0]] = localnodes

    return mesh

# Function bcdictionary creates the 3 dictionaries
#
# - node_dic for the section 'DNODE-NODE TOPOLOGY',
# - line_dic for the section 'DNODE-LINE TOPOLOGY',
# - surf_dic for the section 'DNODE-SURF TOPOLOGY' and
# - vol_dic for the section 'DNODE-VOL TOPOLOGY'
#
# USAGE:
#   node_dic, line_dic, surf_dic, vol_dic = bcdictionary(sections)
#
def bcdictionary(sections):

    node_dic = {}
    # Check if section has topology
    if 'DNODE-NODE TOPOLOGY' in sections:
        # Check if section is not empty
        if sections['DNODE-NODE TOPOLOGY']:
            for line in Bar('Extract node bc').iter(sections['DNODE-NODE TOPOLOGY']):
                nodeID = int(line[1])
                lineID = int(line[3])
                # Set needs as input a list. Solely an integer would give a TypeError
                try:
                    node_dic[lineID].update([nodeID])
                except KeyError:
                    node_dic[lineID] = set([nodeID])

    line_dic = {}
    # Check if section has topology
    if 'DLINE-NODE TOPOLOGY' in sections:
        # Check if section is not empty
        if sections['DLINE-NODE TOPOLOGY']:
            for line in Bar('Extract line bc').iter(sections['DLINE-NODE TOPOLOGY']):
                nodeID = int(line[1])
                lineID = int(line[3])
                # Set needs as input a list. Solely an integer would give a TypeError
                try:
                    line_dic[lineID].update([nodeID])
                except KeyError:
                    line_dic[lineID] = set([nodeID])

    surf_dic = {}
    if 'DSURF-NODE TOPOLOGY' in sections:
        # Check if section is not empty
        if sections['DSURF-NODE TOPOLOGY']:
            for line in Bar('Extract surf bc').iter(sections['DSURF-NODE TOPOLOGY']):
                nodeID = int(line[1])
                surfID = int(line[3])
                try:
                    surf_dic[surfID].update([nodeID])
                except KeyError:
                    surf_dic[surfID] = set([nodeID])

    vol_dic = {}
    if 'DVOL-NODE TOPOLOGY' in sections:
        # Check if section is not empty
        if sections['DVOL-NODE TOPOLOGY']:
            for line in Bar('Extract vol bc').iter(sections['DVOL-NODE TOPOLOGY']):
                # strings are used here, because integer would give an error in Set later on
                nodeID = int(line[1])
                volID = int(line[3])
                try:
                    vol_dic[volID].update([nodeID])
                except KeyError:
                    vol_dic[volID] = set([nodeID])

    return node_dic, line_dic, surf_dic, vol_dic

# Function for collecting node values on the design surface
#
#  INPUT
#    bc_top_            Dictionary of Sets created via bcdictionary
#    desired_ids_        List of desired id, which should be collected; if not given all values will be chosen
#
#  OUTPUT
#    desired_ids_        Resulting list of node ids
#
def collect_all_bc_top_nodes(bc_top_, desired_ids_='All'):

    # Collect all IDs if value is not given
    if 'All'==desired_ids_:
        desired_ids_ = bc_top_.keys()

    global_bc_nodes_ = set()

    #for bc_id, bc_value in bc_top_.iteritems():
    for bc_id in bc_top_.iterkeys():
        if bc_id in desired_ids_:
            global_bc_nodes_.union(bc_top_[bc_id])

    return global_bc_nodes_