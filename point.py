"""Smart points for a graphics context"""

from math import sqrt
from spaces import Space2D

class Compass(object):
    _norm = lambda x, y: (x/sqrt(2), y/sqrt(2))
    """Object to store directions. Preferred over a dict for clarity."""
    N = up    = (0,1)
    E = right = (1,0)
    S = down  = (0,-1)
    W = left  = (-1, 0)

    NE = upRight   = rightUp   = _norm(+1, +1)
    SE = downRight = rightDown = _norm(+1, -1)
    NW = upLeft    = leftUp    = _norm(-1, +1)
    SW = downLeft  = leftDown  = _norm(-1, -1)

    __call__ = lambda s, a: getattr(s,a)

class Cursor(object):
    """A cursor is a coordinate proxy.
    It is always made by another Cursor or a graphics context"""
    
    compass = Compass()
    _box = Space2D()

    def __init__(self, gc, paper, plot = None, current = None, cursor = (0,0),
                 path=() ):

        # The graphics context enables drawing
        self._gc = gc

        # Three coordinates are always available
        self._paper = paper
        self._plot = plot
        self._path = path

        # Cursor is in current space, and can be transformed
        # to other spaces.
        self._cursor = cursor
        self._current = current if current else paper

    def __call__(self, x, y):
        """Allow absolute coordinate by calling Cursor instances"""
        return Cursor(self._gc, self._paper, self._plot, self._current, (x,y),
                      self._path)


    def _switch_space(self, default):
        """Switch coordinate space"""
        oldSpace = self._current
        newSpace = default
        cursor = self._cursor
        
        cursor = newSpace.from_box(oldSpace.to_box(cursor))
         
        return (self if (oldSpace is newSpace) else
                Cursor(self._gc, self._paper, self._plot, default, cursor,
                       self._path))

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
        return Cursor(self._gc, self._paper, self._plot, self._current,
                      self._cursor, self._path + (self,))

    def move(self, dx, dy):
        """Return a shifted new cursor"""
        cx, cy = self._cursor
        cursor = (cx + dx, cy + dy)
        return Cursor(self._gc, self._paper, self._plot, self._current, cursor,
                      self._path)


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
        return self._clear_path()

    @property
    def cycle(self):
        """Convert to a cycle path and push to context"""
        path = self._path + (self,)
        self._gc.push_path(path, closed=True)
        return self._clear_path()

    @property
    def pos(self):
        if self._paper is self._current:
            return self._cursor
        else:
            return self.paper.pos()

    def draw(self):
        if self._path:
            self.end.draw()
        else:
            self._gc.draw()

    def filldraw(self):
        if self._path:
            self.end.filldraw()
        else:
            self._gc.filldraw()

    def fill(self):
        if self._path:
            self.end.fill()
        else:
            self._gc.fill()

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

    def rect(self):
        """Create a rectangle from the last two points of path"""
        a = self._path[-1].paper
        x1, y1 = a._cursor
        c = self.paper
        x2, y2 = c._cursor
        b = a(x1,y2)
        d = c(x2,y1)
        self._gc.push_path([a, b,c,d], True)
        return self._clear_path()

    def __repr__(self):
        return '<Cursor(%g,%g)>' % self._cursor

    def __getattr__(self, attr):
        """Allows compass points to be used"""
        try:
            dx, dy = self.compass(attr)
            return lambda d: self.move(d * dx, d * dy)
        except KeyError, e:
            raise AttributeError('Not found')
