"""
Spaces are one-dimensional bijections from real to real. These are bijections to
and from 'box space' -- a relative space where (0, 0) is the bottom left corner
and (1, 1) is the top-right corner of the box. 

"""

from math import log, exp

class Space(object):
    """Bijection class. Stores function and its inverse. If this class is not
    subclassed, it represents the identity bijection f(x) = g(x) = x."""
    def to_box(self, x):
        """Convert from this coordinate space to box coordinates"""
        return x

    def from_box(self, x):
        """Convert from box coordinates to this coordinate space"""
        return x

    def __repr__(self):
        return "<Space>" 

    @property
    def inverse(self):
        """Return a new space which is an inverse of the current one. This swaps
        to_box with from_box. Two inversions return the current space"""
        space = Space()
        space.to_box = self.from_box
        space.from_box = self.to_box
        return space

class LinSpace(Space):
    """Linear Bijection (e.g. y = m*x + c)"""
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
    """A 2D space, composed of two 1D spaces. Defaults to the 2D
    identity space.
    
    """

    def __init__(self, xspace=None, yspace=None):
        """Keyword arguments:
            xspace -- the space of the x-axis (default Space())
            yspace -- the space of the y-axis (default Space())
            
        """
        self.xspace = xspace if xspace else Space()
        self.yspace = yspace if yspace else Space()

    def to_box(self, p):
        """Convert 2D point p = (x, y) to 2D box space."""
        x, y = p
        return (self.xspace.to_box(x), self.yspace.to_box(y))

    def from_box(self, p):
        """Convert 2D point p = (x, y) from 2D box space."""
        x, y = p
        return (self.xspace.from_box(x), self.yspace.from_box(y))

    @property
    def inverse(self):
        """A 2D space with both x and y spaces inverted."""
        return Space2D(self.xspace.inverse, self.yspace.inverse)

    def append(self, other):
        """Return a ComposedSpace consisting of this space and another
        one.
        
        """
        return ComposedSpace(self, other)

    def __repr__(self):
        return "<Space2D (%r, %r)>" % (self.xspace, self.yspace)

class LinSpace2D(Space2D):
    """2D space composed of two linear 1D spaces. Most common 2D
    space.
    
    """
    def __init__(self, x1, y1, x2, y2):
        Space2D.__init__(self, LinSpace(x1, x2), LinSpace(y1, y2))

# An alias for a duplicated BoxSpace class.
BoxSpace = Space2D

class ComposedSpace(Space2D):
    """2D Space of composed 2D bijections."""
    def __init__(self, *kws):
        self._spaces = tuple(kws)

    def to_box(self, x):
        """Convert point p = (x, y) to 2D box space"""
        for space in reversed(self._spaces):
            x = space.to_box(x)
        return x

    def from_box(self, x):
        """Convert point p = (x, y) from 2D box space"""
        for space in self._spaces:
            x = space.from_box(x)
        return x

    def append(self, other):
        """Return a new composed 2D space according to the identity: 
        
        >>> f.append(g).from_box(p) == g.from_box(f.from_box(p))
        
        """ 

        return ComposedSpace(*(self._spaces + (other,)))
