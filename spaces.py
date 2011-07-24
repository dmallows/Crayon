from math import log, exp

class Space(object):
    """Bijection class. Stores function and its inverse"""
    def to_box(self, x):
        """Convert to box coordinates"""
        return x

    def from_box(self, x):
        """Convert from box coordinates"""
        return x

    def __repr__(self):
        return "<Space>" 

    @property
    def inverse(self):
        l = Space()
        l.to_box = self.from_box
        l.from_box = self.to_box
        return l

class LinSpace(Space):
    """Logarithmic Bijection"""
    def __init__(self, a, b):
        self.params = a, b
        self.a = a
        self.range = range = b - a
        self.m = 1.0 / range 

    def to_box(self, x):
        return self.m * (x - self.a)
    
    def from_box(self, x):
        return self.range*x + self.a 

    def __repr__(self):
        return "<LinSpace (%g, %g)>" % self.params


class LogSpace(Space):
    """Logarithmic Bijection"""
    def __init__(self, a, b):
        self.params = a, b
        self.m = m = 1.0 / a
        self.d = d = log(m * b)
        self.A = 1.0 / d
        self.C = a

    def to_box(self, x):
        return self.A*log(self.m*x)
            
    def from_box(self, x):
        return self.C*exp(self.d*x)

    def __repr__(self):
        return "<LogSpace (%g, %g)>" % self.params

class Space2D(object):
    """2D space and inverse mechanisms"""
    def __init__(self, xspace=None, yspace=None):
        self.xspace = xspace if xspace else Space()
        self.yspace = yspace if yspace else Space()

    def to_box(self, p):
        x, y = p
        return (self.xspace.to_box(x), self.yspace.to_box(y))

    def from_box(self, p):
        x, y = p
        return (self.xspace.from_box(x), self.yspace.from_box(y))

    def __repr__(self):
        return "<Space2D (%r, %r)>" % (self.xspace, self.yspace)

class BoxSpace(object):
    def to_box(self, p):
        return p
    def from_box(self, p):
        return p
