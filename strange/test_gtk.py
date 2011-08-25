import gtk
import cairo
import rsvg

class GraphWindow(object):
    """Handles the scaling from paper space to device space
    using magic."""

    def __init__(self):
        self.window = window = gtk.Window()
        window.set_title('plot')
        self.da = gtk.DrawingArea()
        self.da.set_size_request(600,500)
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

        return False

    def show(self):
        self.da.connect('expose-event', self.redraw)
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.show_all()
        gtk.main()

if __name__=='__main__':

    win = GraphWindow()
    win.show()

