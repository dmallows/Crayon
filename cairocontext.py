from math import pi
from spaces import Space2D, LinSpace, BoxSpace

# We really need to know exactly how wide each string will be, so that when it
# is placed within a box, the box can be resized accordingly.

class CairoContext(object):
    """Low-level stateful graphics context"""
    def __init__(self,context, width, height):
        paper = Space2D(LinSpace(0,width),LinSpace(0, height))
        self._scopes = dict(box = BoxSpace(), paper = paper, absolute=paper)
        self._default = paper
        self.context = context

    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        c = self.context
        c.move_to(*markers[0].absolute.pos)
        for m in markers:
            c.line_to(*m.absolute.pos)

    def cursor(self):
        return Cursor(self, self._scopes, self._default)
    
    def push_circle(self, centre, radius):
        """Draws a circle"""
        x, y = centre.absolute.pos
        c = self.context
        c.arc(x, y, radius, 0, 2*pi)

    def draw(self, **kw):
        self.context.stroke()

    def fill(self, **kw):
        self.context.fill()

    def filldraw(self, **kw):
        self.context.fillstroke()

    def text(self, pos, label, anchor=None):
        self.textcache.add
