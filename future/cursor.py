"""Mutable 2D point system

"""

from __future__ import division
import math
import contextlib

class Mover(object):
    __slots__ = ('_dx', '_dy')

    def __init__(self, dx, dy):
        self._dx = dx
        self._dy = dy

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
        self._angle = math.atan2(dy, dx)
        self._x += dx
        self._y += dy
        return self
    
    @property
    def angle(self):
        return (90 - math.degrees(self._angle)) % 360

    @contextlib.contextmanager
    def clip(self):
        """Takes that path, and clips to it. Returns a contextmanager.
        eg,

        >>> with cr.cursor(0,0).to(10,10).rect.clip as c:
        ...     c(-10,-10).to(10,10).line.draw()
        """
        print "save"
        #self._context.save()
        yield
        print "restore"
        #self._context.restore()

    def head(self, x):
        self._angle = math.radians(90 - x)
        return self

    def forward(self, d):
        dx = d*math.cos(self._angle)
        dy = d*math.sin(self._angle)
        return lambda: self.move(dx, dy)

    def lt(self, dt):
        """Turn right (clockwise) by `dt` degrees"""
        self._angle += math.radians(dt)

    def rt(self, dt):
        """Turn right (clockwise) by `dt` degrees"""
        self._angle -= math.radians(dt)

    """
    def sweep(self, dt):
        'Sweep by `dt` counterclockwise using current point as pivot'
        self._angle -= math.radians(dt)

    def curve_right(self, radius, dt):
        t1 = self._angle
        self.rt(dt)
        t2 = self._angle

    def curve_left(self, radius, dt):
        self._angle += math.radians(dt)
    """

    @property
    def to(self):
        self._path.append(self.pos)
        return self

    @property
    def point(self, bearing):
        return self

    @property
    def clone(self):
        return Cursor(self._x, self._y)

    def __getitem__(self, key):
        try:
            t = self._spaces[key]
            return self._switch_space(
        except KeyError, e:
            raise KeyError("Space %r does not exist!" % key)

    def __call__(self, x, y):
        self._angle = math.atan2(y-self._y, x - self._x)
        self._x = x
        self._y = y
        return self

    def __repr__(self):
        return '<%s%r>' % (self.__class__.__name__, (self._x, self._y))
