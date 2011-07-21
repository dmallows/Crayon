from collections import deque
from exceptions import RuntimeError
import numpy as np
from math import sqrt, log
import cairo

class Pen(object):
    def __init__(self, color=(0,0,0), linewidth=1):
        self.color = color
        self.linewidth = linewidth

    def set_rgb(self, r,g,b):
        """Set the current colour"""
        self.color = (r, g, b)

    def set_linewidth(self, linewidth):
        """Set the current linewidth"""
        self.linewidth = linewidth

isqrt2 = 1.0/sqrt(2)

class Cursor(object):
    """A cursor is a coordinate proxy.
    It is always made by another Cursor"""
    
    _compass = dict(up = (0,1), down = (0,-1), right = (1,0), left = (-1, 0),
                    upLeft = (-isqrt2, isqrt2), upRight = (isqrt2, isqrt2),
                    downLeft = (-isqrt2, -isqrt2), downRight = (isqrt2, -isqrt2))

    def __init__(self, paper, plot = None, default = None ):
        if not default:
            default = paper
        self._paper = paper
        self._plot = plot
        self._default = default
        self._origin = default.bake(0,0)

    def set_default(self, default):
        return Cursor(self._paper, self._plot, default=default)

    @property
    def paper(self):
        return self.set_default(self._paper)

    @property
    def plot(self):
        if self._plot:
            return self.set_default(self._plot)
        else:
            raise RuntimeError('Plot has not been set')

    def move(self, x, y):
        """Return a shifted new cursor"""
        paper, plot, default = self._paper, self._plot, self._default

        if paper is default:
            paper = default = paper.translate(x,y)
        elif plot is default:
            plot = default = plot.translate(x,y)
        else:
            raise AttributeError('Default is not a current coordinate space')

        return Cursor(paper, plot, default)

    def compass(self, dir):
        dx, dy = self._compass[dir]
        return lambda d: self.move(d * dx, d * dy) 

    def __getattr__(self, attr):
        try:
            return self.compass(attr)
        except KeyError, e:
            raise AttributeError('Not found')

    def __repr__(self):
        return '<Cursor %r>' % (self._origin, )

class Coordinates(object):
    """Handles multiple coordinate systems"""
    def __init__(self, transforms = ()):
        self._transforms = tuple(transforms)
    
    def bake(self, x, y):
        """Convert current space into absolute
        space"""
        for f in reversed(self._transforms):
            x, y = f(x, y)
        return (x, y)

    def translate(self, dx, dy):
        # Translate by dx, dy.
        return self.transform(lambda x,y: (x+dx, y+dy))

    def transform(self, f):
        return Coordinates(self._transforms + (f,))

    def scale(self, sx, sy):
        # Scale by sx, sy
        return self.transform(lambda x, y: (x*sx, y*sy))

a = Coordinates((lambda x, y: (10*x, 100*log(1+y)),))
c = Cursor(Coordinates(), a)
