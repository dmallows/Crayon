print "Load ctypes"
from ctypes import *

a=CDLL('/usr/lib/liblapack.so')

def ctypes_solve(m,b):
    m = (c_double*9)(*m)
    b = (c_double*3)(*b)
    print list(m)

    n = len(b)

    p=(c_int*n)()
    size=c_int(n)
    ones=c_int(1)
    ok=c_int(0)
    a.dgesv_(byref(size),byref(ones),m,
             byref(size),p,b,byref(size),byref(ok))

    return list(b)

class Affine2D(object):
    def __init__(self, matrix=None):
        self.matrix = [1,0,0,
                       0,1,0,
                       0,0,1] if matrix is None else matrix

    def __mul__(self, other):
        m = self.matrix
        o = other.matrix
        rows = [m[0:3], m[3:6], m[6:9]]
        cols = [[o[0],o[3],o[6]],
                [o[1],o[4],o[7]],
                [o[2],o[5],o[8]]]

        new = []

        for row in rows:
            for col in cols:
                s = sum(i*j for i,j in zip(row, col))
                print s

        return Affine2D(new)

    def __repr__(self):
        return repr(self.matrix)

    


m = [2,0,0,0,2,0,0,0,1]
b = [5,3,1]
p = ctypes_solve(m,b)

a = Affine2D()
b = Affine2D(m)
