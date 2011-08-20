from math import pi
from crayon.spaces import Space2D, LinSpace, BoxSpace
from crayon.latex import TexRunner

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

import gtk
import cairo
import rsvg

class GraphWindow(object):
    """Handles the scaling from paper space to device space
    using magic."""

    # Magic number for converting between TeX pt and mm.
    _ratio = 0.351459804

    def __init__(self):
        self.window = window = gtk.Window()
        window.set_title('plot')
        self.da = gtk.DrawingArea()
        self.window.add(self.da)
        self.paper_size = 80.0,60.0

    def redraw(self, da, clip):
        c = da.window.cairo_create()

        w, h  = da.window.get_size()

        c.move_to(0,0)
        c.set_source_rgb(0,0,0)
        c.rectangle(0,0,w,h)

        pw, ph = self.paper_size
        ratio = min(w/pw, h/ph)

        nw, nh = pw*ratio, ph*ratio
        dw, dh = w - nw, h - nh
        hdw, hdh = 0.5*dw, 0.5*dh

        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_width(0.2)

        c.translate(hdw, hdh)
        c.scale(ratio, ratio)
        c.fill()

        c.set_source_rgb(1,1,1)
        c.rectangle(0,0,*self.paper_size)
        c.fill()

        c.set_source_rgb(0.5,0.5,0.5)
        c.rectangle(10,10, 60, 40)
        c.stroke()

        return False

    def show(self):
        self.da.connect('expose-event', self.redraw)
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.show_all()
        gtk.main()

if __name__=='__main__':

    win = GraphWindow()
    win.show()

