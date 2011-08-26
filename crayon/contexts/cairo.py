from math import pi, radians, sin, cos
from crayon.spaces import Space2D, LinSpace, BoxSpace
from crayon.point import Cursor
from crayon.color import Rgb
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
    north = (0.5, 1),
    east = (1, 0.5),
    middle = (0.5, 0.5),
    south = (0.5, 0),
    southeast = (1, 0),
    southwest = (0, 0),
    west = (0, 0.5),
    northwest = (0, 1),
    northeast = (1, 1))

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

    def draw(self, color=None, width=None):
        self.context.save()
        if color:
            self.context.set_source_rgb(*color.rgb.color)
        if width:
            self.context.set_line_width(width)
        self.context.stroke()
        self.context.restore()

    def fill(self, fillcolor=None, width=None):
        self.context.save()
        if fillcolor:
            self.context.set_source_rgb(*fillcolor.rgb.color, width=None)
        if width:
            self.context.set_line_width(width)
        self.context.fill()
        self.context.restore()

    def filldraw(self, fillcolor=None, color=None, width=None):
        self.context.save()
        if fillcolor:
            self.context.set_source_rgb(*fillcolor.rgb.color)

        self.context.fill_preserve()

        self.context.restore()
        self.context.save()

        if width:
            self.context.set_line_width(width)

        if color:
            self.context.set_source_rgb(*fillcolor.rgb.color)
        self.context.draw()
        self.context.restore()

    def text(self, pos, label, anchor='middle', color=None, rotation=None):
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

        y0, ymin, xmin, ymax, xmax, yn = tex.extents


        height = ymax - ymin
        width = xmax - xmin
        sx, sy = anchor

        dx, dy = -sx*width-xmin, -(1.0 - sy)*height-ymin

        if rotation:
            angle = radians(-rotation)
            sa, ca = sin(angle), cos(angle)
            c.translate(ca*dx - sa*dy, sa*dx + ca*dy)
            c.rotate(angle)
        else:
            c.translate(dx, dy)

        #c.rectangle(0, ymin, width, height)
        #c.stroke()

        #c.scale(PT2TP, PT2TP)
        #c.scale(90/96.0, 90/96.0)
        tex.svg.render_cairo(c)
        surface = c.pop_group()
        if color:
            c.set_source_rgb(*color.rgb.color)
        c.mask(surface)
        c.restore()

    def make_strings(self, strings):
        self._texes = self._texrenderer.render(strings)
        for t in self._texes:
            y0, ymin, xmin, ymax, xmax, y1 = t.extents
            t.size = TP2MM * (xmax - xmin), TP2MM * (ymax - ymin)
        return self._texes

    def make_svgs(self):
        texes = self._texrenderer.to_svg(self._texes)
        for tex in texes:
            if not hasattr(tex, 'svg'):
                tex.svg = rsvg.Handle(file=tex.svgfile)
