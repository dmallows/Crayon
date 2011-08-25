from math import pi
from crayon.spaces import Space2D, LinSpace, BoxSpace
from crayon.point import Cursor
import rsvg

# We really need to know exactly how wide each string will be, so that when it
# is placed within a box, the box can be resized accordingly.

MM2TP = 72.27 / 25.4
TP2MM = 25.4 / 72.27
MM2PT = 72.0 / 25.4
PT2MM = 25.4 / 72.0
TP2PT = 72.0 / 72.27
PT2TP = 72.27 / 72.0

anchors = dict(
    north = (0.5, 0),
    east = (1, 0.5),
    middle = (0.5, 0.5))

class CairoCanvas(object):
    """Low-level stateful graphics context"""
    def __init__(self, context, texrenderer, width, height):
        self._height = height
        paper = Space2D(LinSpace(0,width),LinSpace(0, height))
        self._scopes = dict(box = BoxSpace(), paper = paper, absolute=paper)
        self._default = paper
        self.context = context
        self._textcache = set()
        self._texrenderer = texrenderer
        #context.scale(MM2TP, MM2TP)
        context.set_line_width(0.2)
        context.set_line_cap(1)
        context.set_line_join(1)
    
    def user_to_device(self, marker):
        x, y = marker.absolute.pos
        pos = (x, self._height - y)
        return pos

    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        c = self.context
        c.move_to(*self.user_to_device(markers[0]))
        for m in markers:
            c.line_to(*self.user_to_device(m))
        if closed:
            c.close_path()

    def cursor(self):
        return Cursor(self, self._scopes, self._default)
    
    def push_circle(self, centre, radius):
        """Draws a circle"""
        x, y = self.user_to_device(centre)
        c = self.context
        c.arc(x, y, radius, 0, 2*pi)

    def draw(self, **kw):
        self.context.stroke()

    def fill(self, **kw):
        self.context.fill()

    def filldraw(self, **kw):
        self.context.fillstroke()

    def text(self, pos, label, anchor='middle'):
        x,y = self.user_to_device(pos)
        anchor = anchors[anchor]
        texes = self._texrenderer.render([label])
        tex, = self._texrenderer.to_svg(texes)
        s = TP2MM
        c = self.context
        c.save()
        c.translate(x,y)
        c.push_group()
        c.scale(s,s)
        # I'm not sure if this *is* needed
        y0, ymin, xmin, ymax, xmax, yn = [PT2TP * i for i in tex.extents]


        height = ymax - ymin
        width = xmax - xmin
        print width, height
        c.translate(-xmin, -ymin)
        dx, dy = anchor

        c.set_line_width(0.05)
        c.translate(-dx*width, -dy*height)
        #c.rectangle(0, ymin, width, height)
        #c.stroke()

        s = rsvg.Handle(file=tex.svgfile)
        #c.scale(PT2TP, PT2TP)
        #c.scale(90/96.0, 90/96.0)
        s.render_cairo(c)
        surface = c.pop_group()
        c.set_source_rgb(0,0,0)
        c.mask(surface)
        c.restore()
        
    def make_text(self):
        self.texrenderer.to_svg(texes)

