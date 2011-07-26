"""Smart points for a graphics context"""

from math import sqrt
from spaces import Space2D, LinSpace2D, LinSpace

class Compass(object):
    _norm = lambda x, y: (x/sqrt(2), y/sqrt(2))
    """Object to store directions. Preferred over a dict for clarity."""
    N = up    = (0,1.)
    E = right = (1.,0)
    S = down  = (0,-1.)
    W = left  = (-1., 0)

    NE = upRight   = rightUp   = _norm(+1, +1)
    SE = downRight = rightDown = _norm(+1, -1)
    NW = upLeft    = leftUp    = _norm(-1, +1)
    SW = downLeft  = leftDown  = _norm(-1, -1)

    __getitem__ = lambda s, a: getattr(s,a)

class Cursor(object):
    """A cursor is a coordinate proxy.  It is always made by another Cursor or a
    graphics context"""
    
    compass = Compass()
    
    def __init__(self, gc, spaces, current, cursor = (0,0), path=(), zooms=()):
        # The graphics context enables drawing
        self._gc = gc

        # The current path that is being drawn
        self._path = path

        self._spaces = spaces
        self._zooms = zooms

        # Cursor is in current space, and can be transformed
        # to other spaces.
        self._cursor = cursor
        self._current = current if current else paper

    def __call__(self, x, y):
        """Allow absolute coordinate by calling Cursor instances"""
        return self.set(cursor = (x,y))

    def __getattr__(self, attr):
        """Allows compass points to be used"""
        try:
            dx, dy = self.compass[attr]
            return lambda d: self.move(d * dx, d * dy)
        except AttributeError, e:
            return self._switch_space(attr)

    def set(self, spaces = None, current = None, cursor = None, path = None,
            zooms = None):
        spaces  = self._spaces  if spaces  is None else spaces
        current = self._current if current is None else current
        cursor  = self._cursor  if cursor  is None else cursor
        path    = self._path    if path    is None else path
        zooms   = self._zooms   if zooms   is None else zooms
    
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
        
    def zoom(self):
        # This entire function is built from distilled voodoo...
        # Nobody is sure how it works...
        # Touch it, nobody knows what will happen...
        # No, seriously, I have no clue how this works.

        a = self._path[-1]
        b = self

        # Rescale the box so it sits in [(0,0):(1,1)]
        x1, y1 = a.box._cursor
        x2, y2 = b.box._cursor

        # Now, what would we have to do to undo such a transformation?
        spaces = self._spaces.copy()
        boxspace = spaces['box'].append(LinSpace2D(x1, y1, x2, y2).inverse)

        spaces['box'] = boxspace

        k = self.set(spaces=spaces)

        x1, y1 = a.paper._cursor
        x2, y2 = b.paper._cursor

        dx, dy = x2 - x1, y2 - y1

        spaces['paper'] = boxspace.append(LinSpace2D(0,0,dx,dy))

        return self._clear_path().set(spaces=spaces)

    def set_plot(self, plot):
        spaces = self._spaces.copy()
        spaces['plot'] = spaces['box'].append(plot)
        return self.set(spaces=spaces)

    def clear_plot(self):
        spaces = self._spaces.copy()
        del spaces['plot']

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
        return self._cursor

    def x(self, x):
        _, y = self.pos
        return self.set(cursor = (x, y))

    def y(self, y):
        x, _ = self.pos
        return self.set(cursor = (x, y))

    def draw(self, *a, **kw):
        """Draw the currently stored path"""
        if self._path:
            return self.end.draw(*a, **kw)
        else:
            self._gc.draw(*a, **kw)
            return self._clear_path()

    def filldraw(self, *a, **kw):
        """Fill and draw the currently stored path"""
        if self._path:
            return self.end.filldraw(*a, **kw)
        else:
            self._gc.filldraw(*a, **kw)
            return self._clear_path()

    def text(self, label, anchor=None):
        self._gc.text(self, label, anchor)
        return self

    def fill(self, *a, **kw):
        """Fill the currently stored path"""
        if self._path:
            return self.end.fill(*a, **kw)
        else:
            self._gc.fill(*a, **kw)
            return self._clear_path()

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

    def __repr__(self):
        return '<Cursor(%g,%g)>' % self._cursor

