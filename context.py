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

def _to_box(space, point):
    print space
    X, Y = space
    x, y = point
    return (X.to_box(x), Y.to_box(y))

def _from_box(space, point):
    print space
    X, Y = space
    x, y = point
    return (X.from_box(x), Y.from_box(y))

class Coordinates(object):
    """Handles multiple coordinate systems"""
    def __init__(self, transforms = ()):
        self._transforms = tuple(transforms)
    
    def to_box(self, x):
        """Convert coordinate in current space into box space"""
        for f,_ in reversed(self._transforms):
            x = f(x)
        return x

    def from_box(self, x):
        """Convert coord into current space from box space"""
        for _,g in self._transforms:
            x = g(x)
        return x


class Cursor(object):
    """A cursor is a coordinate proxy.
    It is always made by another Cursor"""
    
    _compass = dict(up = (0,1), down = (0,-1), right = (1,0), left = (-1, 0),
                    upLeft = (-isqrt2, isqrt2), upRight = (isqrt2, isqrt2),
                    downLeft = (-isqrt2, -isqrt2), downRight = (isqrt2, -isqrt2))

    _null = Coordinates()
    _box = (_null, _null)

    def __init__(self, paper, plot = None, current = None, cursor = (0,0) ):

        if not current:
            current = paper

        self._paper = paper
        self._plot = plot

        # Cursor is in current space, and can be transformed
        # to other spaces.
        self._cursor = cursor
        self._current = current

    def _switch_space(self, default):
        oldSpace = self._current
        newSpace = default
        cursor = self._cursor
        
        cursor = _from_box(newSpace , _to_box(oldSpace, cursor))
        
        return Cursor(self._paper, self._plot, default, cursor)

    @property
    def paper(self):
        return self._switch_space(self._paper)

    @property
    def plot(self):
        if self._plot:
            return self._switch_space(self._plot)
        else:
            raise RuntimeError('Plot has not been set')
        
    @property
    def box(self):
        return self._switch_space(self._box)

    def move(self, dx, dy):
        """Return a shifted new cursor"""
        cx, cy = self._cursor
        cursor = (cx + dx, cy + dy)
        return Cursor(self._paper, self._plot, self._current, cursor)

    def __call__(self, x, y):
        return Cursor(self._paper, self._plot, self._current, (x,y))

    def compass(self, dir):
        dx, dy = self._compass[dir]
        return lambda d: self.move(d * dx, d * dy) 

    def __getattr__(self, attr):
        try:
            return self.compass(attr)
        except KeyError, e:
            raise AttributeError('Not found')

    def __repr__(self):
        return '<Cursor(%g,%g)>' % self._cursor


from bijections import lin_bijection, log_bijection

paper = Coordinates((lin_bijection(0,800),))
log = Coordinates((log_bijection(10,1000),))
plot = Coordinates((lin_bijection(0,400),))

c = Cursor((paper, paper), (plot, log))
