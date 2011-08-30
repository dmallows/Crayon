"""Mutable 2D point system

"""

from __future__ import division
import math
import contextlib

class Mover(object):
    """Represent a direction for moving by a given amount."""
    def __init__(self, dx, dy):
        self._dx = dx
        self._dy = dy
        self.__doc__ = "Return function f(d) that moves by d*({0}, {1})".\
                format(self._dx, self._dy)

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
    def __get__(self, ins, owner):
        if ins is None:
            return self
        else:
            return lambda d: ins.move(d*self._dx, d*self._dy)

    def __set__(self, instance, value):
        raise AttributeError('Cannot set attribute')
    
    def __add__(self, other):
        return other.add(self._dx, self._dy)

    def __repr__(self):
        return 'lol'

class ChangeView(object):
    """A `descriptor` that removes much boilerplate"""
    def __init__(self, spacename):
        self._spacename = spacename
        self.__doc__ = 'Transform this cursor to the {0} space'.\
                        format(self._spacename)

    def __get__(self, ins, owner):
        if ins is None:
            return self
        else:
            return ins._switch_space(ins[self._spacename])

    def __set__(self, ins, val):
        raise AttributeError('Attribute not settable')

    def __repr__(self):
        return "ChangeView(%r)" % self._spacename

class Cursor(object):
    # BEGIN Magic
    # These are class members that represent a deferred relative motion.
    # Somebody calls c.N(10), where c is an instance of cursor, and the cursor
    # moves `north' by 10 units in the current space.

    N = north = up = Mover(0, 1)
    E = east = right = Mover(1, 0)
    S = south = down = Mover(0, -1)
    W = west = left = Mover(-1, 0)

    NE = (N + E).norm()
    NW = (N + W).norm()
    SE = (S + E).norm()
    SW = (S + W).norm()

    box = ChangeView('box')
    paper = ChangeView('paper')
    absolute = ChangeView('absolute')
    # END Magic 

    def __init__(self, context, spaces, current, pos = (0,0), path=None):
        self.pos = pos
        self._context = context
        self._spaces = spaces.copy()
        self._current = current
        # assert current in spaces.values()
        self._path = [] if path is None else path

    def copy(self, cls=None):
        cls = self.__class__ if cls is None else cls
        return cls(self._context,
                   self._spaces,
                   self._current,
                   self.pos,
                   self._path)

    # --------------
    # Basic movement
    # ==============
    #
    # Note that call is implemented to move to a given x, y coordinate pair.
    # This is for the benefit of inline calling, and helps with pipelining.

    def __call__(self, x, y):
        """Move to given position x, y"""
        self._angle = math.atan2(y-self._y, x - self._x)
        self._x = x
        self._y = y
        return self

    @property
    def pos(self):
        """The x, y position of the cursor"""
        return (self._x, self._y)

    @pos.setter
    def pos(self, pos):
        self._x, self._y = pos

    def degrees(self):
        """Get the current angle"""
        return (90 - math.degrees(self._angle)) % 360

    def bearing(self, bearing):
        """Set the current bearing"""
        self._angle = math.radians(90 - bearing)
        return self
    
    # Angle needs a getter and setter, since internally it's stored in radians.
    # Show me somebody who thinks 
    degrees = property(degrees, bearing)

    def move(self, dx, dy):
        self._angle = math.atan2(dy, dx)
        self._x += dx
        self._y += dy
        return self

    # Path manipulation
    @property
    def to(self):
        self._path.append(self.pos)
        return self

    def zoom(self):
        a = self.copy().absolute(*self._path.pop())
        b = self
        
        x1, y1 = a.box.pos
        x2, y2 = b.box.pos
        
        cls = self['paper'].__class__
        spaces = self._spaces.copy()
        boxspace = spaces['box'].append(cls(x1, y1, x2, y2).inverse)

        spaces['box'] = boxspace
        self._spaces=spaces

        x1, y1 = a.paper.pos
        x2, y2 = b.paper.pos

        dx = x2 - x1
        dy = y2 - y1

        spaces['paper'] = boxspace.append(cls(0,0,dx,dy))
        return self


    @contextlib.contextmanager
    def clip(self):
        """Takes that path, and clips to it. Returns a contextmanager.
        eg,

        >>> with cr.cursor(0,0).to(10,10).rect.clip as c:
        ...     c(-10,-10).to(10,10).line.draw()
        """
        self._context.save()
        yield
        print "restore"
        self._context.restore()

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

    def _switch_space(self, newSpace):
        """Convert from one space into another"""
        if newSpace is not self._current:
            self.pos = newSpace.from_box(
                self._current.to_box(self.pos))
            self._current = newSpace

        return self

    def __getitem__(self, key):
        try:
            return self._spaces[key]
        except KeyError, e:
            raise KeyError("Space %r does not exist!" % key)

    def __setitem__(self, name, newSpace):
        """Set the space"""
        try:
            if self[name] is self._current:
                self._switch_space(newSpace)
        except KeyError:
            pass
        
        self._spaces[name] = newSpace


    def __repr__(self):
        return '<%s%r>' % (self.__class__.__name__, (self._x, self._y))
