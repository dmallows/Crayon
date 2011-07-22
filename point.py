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

    __getitem__ = lambda s, a: getattr(s,a)

class Cursor(object):
    """A cursor is a coordinate proxy.  It is always made by another Cursor or a
    graphics context"""
    
    compass = Compass()
    
    def __init__(self, gc, spaces, current, cursor = (0,0), path=()):
        # The graphics context enables drawing
        self._gc = gc

        # The current path that is being drawn
        self._path = path

        self._spaces = spaces

        # Cursor is in current space, and can be transformed
        # to other spaces.
        self._cursor = cursor
        self._current = current if current else paper

    def __call__(self, x, y):
        """Allow absolute coordinate by calling Cursor instances"""
        return self.set(cursor = (x,y))

    def set(self, spaces = None, current = None, cursor = None, path = None):
        spaces = self._spaces   if spaces  is None else spaces
        current = self._current if current is None else current
        cursor = self._cursor   if cursor  is None else cursor
        path = self._path       if path    is None else path
    
        return Cursor(self._gc, spaces, current, cursor, path)

    def _lookup_space(self, name):
        try:
            return self._spaces[name]
        except KeyError, e:
            raise Exception('Space %r is undefined' % name)

    def _switch_space(self, newName):
        """Switch coordinate space"""
        newSpace = self._lookup_space(newName)
        oldSpace = self._current

        if newSpace is oldSpace:
            return self

        cursor = newSpace.from_box(oldSpace.to_box(self._cursor))

        return self.set(current = newSpace, cursor = cursor)

    def __dir__(self):
        return

    @property
    def to(self):
        """Add current point to path"""
        path = self._path + (self, ) 
        return self.set(path = path)

    def move(self, dx, dy):
        """Return a shifted new cursor"""
        cx, cy = self._cursor
        cursor = (cx + dx, cy + dy)
        return self.set(cursor = cursor)

    def distance_to(self, other):
        """Distance from cursor to another cursor in paper space"""
        if self is self.paper:
            return other.distance_from(self._cursor)
        else:
            return self.paper.distance_to(other)

    def distance(self):
        return self.distance_to(self._path[-1])

    def distance_from(self, pt):
        """Distance from current cursor to point in paper space"""
        if self is self.paper:
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
        if self is self.paper:
            return self._cursor
        else:
            return self.paper.pos

    def draw(self):
        """Draw the currently stored path"""
        if self._path:
            self.end.draw()
        else:
            self._gc.draw()

    def filldraw(self):
        """Fill and draw the currently stored path"""
        if self._path:
            self.end.filldraw()
        else:
            self._gc.filldraw()

    def fill(self):
        """Fill the currently stored path"""
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
        """Clear the currently stored path"""
        return self.set(path = ())

    @property
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

    def __getattr__(self, attr):
        """Allows compass points to be used"""
        try:
            dx, dy = self.compass[attr]
            return lambda d: self.move(d * dx, d * dy)
        except AttributeError, e:
            return self._switch_space(attr)

    def __repr__(self):
        return '<Cursor(%g,%g)>' % self._cursor

