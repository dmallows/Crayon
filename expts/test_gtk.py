import gtk
import cairo
import rsvg
from parse import PosParser

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
        self.svg = rsvg.Handle(file='full-001.svg')

        p = PosParser()

        self.pos = p.parse('full.pos')[0]

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

        self.draw_text(c)
        return False

    def draw_text(self, c):
        c.save()

        print self.pos
        enter, ymin, xmin, ymax, xmax, exit = self.pos
        height = ymax - ymin
        width  = xmax - xmin
        print width, height

        c.translate(10,0)
        c.scale(self._ratio,self._ratio)
        c.translate(0,-ymin)

        c.rectangle(0,ymin,width,height)
        c.stroke()
        self.svg.render_cairo(c)
        c.set_source_rgb(0,1,0)
        c.move_to(0, enter)
        c.line_to(xmax, enter)
        c.stroke()
        c.set_source_rgb(1,0,0)
        c.move_to(0, exit)
        c.line_to(xmax, exit)
        c.stroke()
        c.restore()

    def show(self):
        self.da.connect('expose-event', self.redraw)
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.show_all()
        gtk.main()

if __name__=='__main__':

    win = GraphWindow()
    win.show()

