# Sets up a cairo context with a gtk window that is updated on show() being
# called. Similar in style to matplotlib...

import gtk
import cairo
from crayon.latex import TexRunner
from crayon.contexts.cairo import CairoCanvas
import plots.layers as layers

class GraphWindow(gtk.Window):
    """Handles the scaling from paper space to device space
    using magic."""

    def __init__(self, tr, plot):
        super(GraphWindow, self).__init__()
        self._plot = plot
        self.set_title('plot')
        self.da = gtk.DrawingArea()
        self.da.set_size_request(600,500)
        self.add(self.da)
        self._paper_size = 80.0,60.0
        self._tr = tr

    def redraw(self, da, clip):
        c = da.window.cairo_create()

        w, h  = da.window.get_size()

        c.move_to(0,0)
        c.set_source_rgb(0,0,0)
        c.rectangle(0,0,w,h)

        pw, ph = self._paper_size
        ratio = min(w/pw, h/ph)

        nw, nh = pw*ratio, ph*ratio
        dw, dh = w - nw, h - nh
        hdw, hdh = 0.5*dw, 0.5*dh

        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_width(1.0)

        c.translate(hdw, hdh)
        c.scale(ratio, ratio)
        c.fill()

        c.set_source_rgb(1,1,1)
        c.rectangle(0,0,*self._paper_size)
        c.fill()


        c.set_source_rgb(0, 0, 0)
        canvas = CairoCanvas(c, self._tr, *self._paper_size)
        self._plot.draw(canvas.cursor())

        return False

    def show(self):
        self.da.connect('expose-event', self.redraw)
        self.connect('destroy', lambda w: gtk.main_quit())
        self.show_all()
        gtk.main()

histo = layers.Histo1D(title='My Pretty Plot')
tr = TexRunner()

def show(plot = None):
    win = GraphWindow(tr, plot)
    try:
        win.show()
    except KeyboardInterrupt, e:
        win.destroy()

