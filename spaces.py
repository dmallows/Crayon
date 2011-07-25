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

    @property
    def inverse(self):
        return Space2D(self.xspace.inverse, self.yspace.inverse)

    def append(self, other):
        return ComposedSpace(self, other)

    def __repr__(self):
        return "<Space2D (%r, %r)>" % (self.xspace, self.yspace)

class LinSpace2D(Space2D):
    def __init__(self, x1, y1, x2, y2):
        Space2D.__init__(self, LinSpace(x1, x2), LinSpace(y1, y2))

class BoxSpace(Space2D):
    def __init__(self):
        Space2D.__init__(self, Space(), Space())

class ComposedSpace(Space2D):
    def __init__(self, *kws):
        self._spaces = tuple(kws)

    def to_box(self, x):
        # Technically this is a reduction
        for space in reversed(self._spaces):
            x = space.to_box(x)
        return x

    def from_box(self, x):
        for space in self._spaces:
            x = space.from_box(x)
        return x

    def append(self, other):
        return ComposedSpace(*(self._spaces + (other,)))
