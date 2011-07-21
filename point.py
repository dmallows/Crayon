"""Smart points for a graphics context"""

from math import sqrt
isqrt2 = 1.0/sqrt(2)

def _to_box(space, point):
    X, Y = space
    x, y = point
    return (X.to_box(x), Y.to_box(y))

def _from_box(space, point):
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
    
    _compass_pt = dict(up = (0,1), down = (0,-1), right = (1,0), left = (-1, 0),
                       upLeft = (-isqrt2, isqrt2), upRight = (isqrt2, isqrt2),
                       downLeft = (-isqrt2, -isqrt2), downRight = (isqrt2, -isqrt2))

    _null = Coordinates()
    _box = (_null, _null)

    def __init__(self, gc, paper, plot = None, current = None, cursor = (0,0),
                 path=() ):

        if not current:
            current = paper

        self._paper = paper
        self._plot = plot
        self._path = path
        self._gc = gc

        # Cursor is in current space, and can be transformed
        # to other spaces.
        self._cursor = cursor
        self._current = current

    def _switch_space(self, default):
        oldSpace = self._current
        newSpace = default
        cursor = self._cursor
        
        cursor = _from_box(newSpace , _to_box(oldSpace, cursor))
        
        return Cursor(self._gc, self._paper, self._plot, default, cursor, self._path)

    @property
    def paper(self):
        """Switch to mm coordinate system"""
        return self._switch_space(self._paper)

    @property
    def plot(self):
        """Switch to space defined by axes of plot"""
        if self._plot:
            return self._switch_space(self._plot)
        else:
            raise RuntimeError('Plot has not been set')
        
    @property
    def box(self):
        """Switch to box space"""
        return self._switch_space(self._box)

    @property
    def to(self):
        """Add current point to path"""
        return Cursor(self._gc, self._paper, self._plot, self._current, self._cursor, self._path
                     + (self,))

    def move(self, dx, dy):
        """Return a shifted new cursor"""
        cx, cy = self._cursor
        cursor = (cx + dx, cy + dy)
        return Cursor(self._gc, self._paper, self._plot, self._current, cursor, self._path)

    def __call__(self, x, y):
        return Cursor(self._gc, self._paper, self._plot, self._current, (x,y), self._path)

    def _compass(self, dir):
        """Helper for moving relative to cursor"""
        dx, dy = self._compass_pt[dir]
        return lambda d: self.move(d * dx, d * dy) 

    def __getattr__(self, attr):
        try:
            return self._compass(attr)
        except KeyError, e:
            raise AttributeError('Not found')

    def distance_to(self, other):
        """Distance from cursor to another cursor in paper space"""
        if self._current is self._paper:
            return other.distance_from(self._cursor)
        else:
            return self.paper.distance_to(other)

    def distance(self):
        return self.distance_to(self._path[-1])

    def distance_from(self, pt):
        """Distance from current cursor to point in paper space"""
        if self._current is self._paper:
            x1, y1 = self._cursor
            x2, y2 = pt
            dx, dy = x1 - x2, y1 - y2
            return sqrt(dx*dx + dy*dy)
        else:
            return self.paper.distance_from(other)
        
    @property
    def end(self):
        """Convert to a path and push to context"""
        path = self._path + (self,)
        self._gc.push_path(path, closed=False)
        return self.clear()

    @property
    def cycle(self):
        """Convert to a cycle path and push to context"""
        path = self._path + (self,)
        self._gc.push_path(path, closed=True)
        return self.clear()


    def stroke(self):
        self._gc.stroke()

    def circle(self):
        """Create a circle from the last two points of the path and push to
        stack"""
        centre = self._path[-1]
        radius = self.distance()
        self._gc.push_circle(centre, radius)
        return self._clear_path()

    def _clear_path(self):
        return Cursor(self._gc, self._paper, self._plot, self._current,
                      self._cursor, ())

    def rectangle(self):
        """Create a rectangle from the last two points of path"""
        a = self._path[-1]
        b = self
        self._gc.push_path(path, closed=True)
        return self._clear_path()

    def __repr__(self):
        return '<Cursor(%g,%g)>' % self._cursor

from bijections import lin_bijection, log_bijection
from point import Cursor
from context import Context

gc = Context()

paper = Coordinates((lin_bijection(0,800),))
log = Coordinates((log_bijection(10,1000),))
plot = Coordinates((lin_bijection(0,400),))

c = Cursor(gc, (paper, paper), (plot, log))

