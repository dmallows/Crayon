"""Smart, immutable points which act as a 'remote control' for a
graphics context

"""

from math import sqrt
from spaces import Space2D, LinSpace2D, LinSpace

class Compass(object):
    _norm = lambda x, y: (x/sqrt(2), y/sqrt(2))
    """Object to store directions. Preferred over a dict for clarity and
    for making a more pythonic API."""
    N = up    = (0,1.)
    E = right = (1.,0)
    S = down  = (0,-1.)
    W = left  = (-1., 0)

    NE = upRight   = rightUp   = _norm(+1, +1)
    SE = downRight = rightDown = _norm(+1, -1)
    NW = upLeft    = leftUp    = _norm(-1, +1)
    SW = downLeft  = leftDown  = _norm(-1, -1)

    def __getitem__(self, a):
        try:
            return getattr(self, a)
        except AttributeError, e:
            raise KeyError('Not in Compass: %s' % a)

class Cursor(object):
    """A cursor is a coordinate proxy.  It is always made by another Cursor or a
    graphics context"""
    
    compass = Compass()
    
    def __init__(self, gc, spaces, current, cursor = (0,0), path=()):
        """Initialise a Point. Most points will be created by the
        stateful graphics context, so constructor is rarely called
        directly.
        
        gc -- A stateful graphics context
        spaces -- A dictionary of 2D spaces
        current -- Current space (Default paper)
        cursor -- (x, y) point of the cursor
        path -- The currently attached path
        """

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
        """Set cursor to coordinate (x, y) in current space"""
        return self._set(cursor = (x,y))

    def __getattr__(self, attr):
        # Proxy the Compass object
        try:
            dx, dy = self.compass[attr]
            return lambda d: self.move(d * dx, d * dy)
        except KeyError, e:
            return self._switch_space(attr)

    def _set(self, spaces = None, current = None, cursor = None, path = None):
        """Return a new Cursor, settin any non-none parameters"""
        path = self._path if path is None else path
        spaces = self._spaces if spaces is None else spaces
        cursor = self._cursor if cursor is None else cursor
        current = self._current if current is None else current
    
        return Cursor(self._gc, spaces, current, cursor, path)

    def _lookup_space(self, name):
        """Lookup space in spaces dictionary"""
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

        return self._set(current = newSpace, cursor = cursor)

    def __dir__(self):
        return

    @property
    def to(self):
        """Return a new cursor with current cursor added to path"""
        path = self._path + (self, ) 
        return self._set(path = path)

    def move(self, dx, dy):
        """Return a shifted new cursor"""
        cx, cy = self._cursor
        cursor = (cx + dx, cy + dy)
        return self._set(cursor = cursor)

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
        """Zoom into the rectangle with diagonal defined by shortest
        path between last point and current cursor. Think multi-
        touch...
        
        """
        # This entire function is built from distilled voodoo...
        # but it seems to work.
        a = self._path[-1]
        b = self

        # Rescale the box so it sits in [(0,0):(1,1)]
        x1, y1 = a.box._cursor
        x2, y2 = b.box._cursor

        # Now, what would we have to do to undo such a transformation?
        spaces = self._spaces.copy()
        boxspace = spaces['box'].append(LinSpace2D(x1, y1, x2, y2).inverse)

        spaces['box'] = boxspace

        k = self._set(spaces=spaces)

        x1, y1 = a.paper._cursor
        x2, y2 = b.paper._cursor

        dx, dy = x2 - x1, y2 - y1

        spaces['paper'] = boxspace.append(LinSpace2D(0,0,dx,dy))

        return self._clear_path()._set(spaces=spaces)

    def set_plot(self, plot):
        """Set current plot space."""
        spaces = self._spaces.copy()
        spaces['plot'] = spaces['box'].append(plot)
        return self._set(spaces=spaces)

    def clear_plot(self):
        """Clear current plot space."""
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
        """Return copy of current cursor with new x"""
        _, y = self.pos
        return self._set(cursor = (x, y))

    def y(self, y):
        """Return copy of current cursor with new y"""
        x, _ = self.pos
        return self._set(cursor = (x, y))

    def draw(self, *a, **kw):
        """Draw the currently stored path - mutates context"""
        if self._path:
            return self.end.draw(*a, **kw)
        else:
            self._gc.draw(*a, **kw)
            return self._clear_path()

    def filldraw(self, *a, **kw):
        """Filldraw the currently stored path - mutates context"""

        if self._path:
            return self.end.filldraw(*a, **kw)
        else:
            self._gc.filldraw(*a, **kw)
            return self._clear_path()

    def text(self, label, anchor=None):
        """Place text at cursor location, using anchor if given"""
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
        # TODO: docstring cleanup!
        """Create a circle with centre and radius the last two points of the path and push to
        stack"""
        centre = self._path[-1]
        radius = self.distance()
        self._gc.push_circle(centre, radius)
        return self._clear_path()

    def _clear_path(self):
        """Clear the currently stored path"""
        return self._set(path = ())

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
