from __future__ import division

import math

class Mover(object):
    __slots__ = ('_dx', '_dy')

    def __init__(self, dx, dy):
        self._dx, self._dy = dx, dy

    def norm(self):
        s = 1.0 / math.hypot(self._dx, self._dy)
        self._dx *= s
        self._dy *= s
        return self

    def add(self, dx, dy):
        return Mover(dx + self._dx, dy + self._dy)

    # We need this to be a descriptor over a callable so we can find which
    # object did the calling. This avoids having to use getattr, which can be
    # used for much more powerful things now.
    def __get__(self, obj, cls, type_=None):
        return lambda d: obj.move(d*self._dx, d*self._dy)
    
    def __add__(self, other):
        return other.add(self._dx, self._dy)

class Angle(object):
    @property
    def degrees(self):
        return math.degrees(self._angle)

    @degrees.setter
    def degrees(self, value):
        self._angle = math.radians(self._angle)
    
    @property
    def radians(self):
        return self._angle

    @radians.setter
    def degrees(self, value):
        self._angle = self._angle

class Cursor(object):
    N = north = up = Mover(0, 1)
    E = east = right = Mover(1, 0)
    S = south = down = Mover(0, -1)
    W = west = left = Mover(-1, 0)
    NE = (N + E).norm()
    NW = (N + W).norm()
    SE = (S + E).norm()
    SW = (S + W).norm()

    def __init__(self, x, y, path=None):
        self._x, self._y = x, y
        self._path = [] if path is None else path

    @property
    def pos(self):
        return (self._x, self._y)

    def move(self, dx, dy):
        self._x0, self._y0 = self._x, self._y
        self._x += dx
        self._y += dy
        return self
    
    @property
    def angle(self):
        x1, y1 = self._path[-1]
        x2, y2 = self._x, self._y
        return math.degrees(math.atan2(y2 - y1, x2 - x1))

    def forward(self, d):
        self.move()

    @property
    def fly(self):
        """Set the angle, but do not draw the path"""

    @property
    def to(self):
        self._path.append(self.pos)
        return self

    def point(self, bearing):
        return self

    @property
    def clone(self):
        return Cursor(self._x, self._y)

    def __call__(self, x, y):
        self._x0 = self._x
        self._y0 = self._x
        self._x = x
        self._y = y
        return self

    def __repr__(self):
        return '<%s%r>' % (self.__class__.__name__, self.__getstate__())
