import math

ceil = lambda x : int(math.ceil(x))
floor = lambda x: int(math.floor(x))
log = math.log

class LinTicker(object):
    """A ticker for linear axes"""
    def __init__(self, space, major, minor):
        major = float(major)
        minor = float(minor)

        self._space = space
        self._range = (space.from_box(0), space.from_box(1))

        self.major = self._calc_major(major)
        self.minor = self._calc_minor(major, minor)

    def _to_str(self, x):
        return '%g' % x

    def _calc_major(self, dx):
        """Major ticks"""
        a, b = self._range
        ticks = (i*dx for i in xrange(ceil(a / dx), int(1 + b/dx)) )
        return tuple((i, self._to_str(i)) for i in ticks)

    def _calc_minor(self, dx, dxm):
        """Minor ticks"""
        a, b = self._range
        ticks = (i*dxm for i in xrange(ceil(a / dxm), int(1 + b/dxm)) )
        return tuple(i for i in ticks if i not in self.major)

class LogTicker(object):
    def __init__(self, space):
        self._space = space
        self._range = (space.from_box(0), space.from_box(1))

        self.major = self._calc_major()
        self.minor = self._calc_minor()

    def _to_str(self, x):
        return '$10^{%d}$' % x

    def _calc_major(self):
        """Major ticks"""
        a, b = self._range
        eps = 0.0001
        a, b = ceil(log(a,10) - eps), floor(log(b,10) + eps)
        a, b = sorted((a,b))
        return [(10**i, self._to_str(i)) for i in xrange(a, b+1)]

    def _calc_minor(self):
        # Concat lists together
        lsum = lambda xs: reduce(lambda x, y: x + y, xs)

        return lsum([0.1*i*x for i in xrange(2,10)] for x,_ in self.major[1:])

from crayon.contexts.tikz import TikzCanvas
from crayon.spaces import LinSpace, LogSpace, Space2D

class Histo(Layer):
    def __init__(self, width=160, height=120):
        Layer.__init__(self)
        self._canvas = TikzCanvas(width, height)

        xspace = LinSpace(0,100)
        yspace = LogSpace(0.001,1000)

        self._space = Space2D(xspace, yspace)

        from math import sin, exp, pi
        xs = (x * 1.0 for x in xrange(0, 100))
        data = [(x, 1.0, exp(6.8*sin(2*pi/100.0*x))) for x in xs]
        
        self.hticks = HTicks(LinTicker(xspace, 20, 1))
        self.vticks = VTicks(LinTicker(yspace))
        self.data = HistoData(data)

    def setup_draw(self, c):
        # self.set_plot()
        return c

    def draw(self):
        c = self._canvas.cursor()
        c.box(0,0).to(1,1).rect.draw()
        c = c.paper(10,10).to.box(1,1).paper.move(-10,-10).zoom()\
                                      .set_plot(self._space)

        #c.box(0,0).to(1,1).rect.fill()
        #print c.plot(0,0.001).absolute
        self.data.draw(c)
        self.hticks.draw(c)
        self.vticks.draw(c)

        c.box(0,0).to(1,1).rect.draw()

    fulldraw = draw

class HTicks(Layer):
    def __init__(self, ticker):
        Layer.__init__(self)
        self._ticker = ticker

    def draw(self, c):
        top = c.box(0,1).plot.x
        bottom = c.box(0,0).plot.x

        for x, label in self._ticker.major:
            top(x).to.box.down(0.02).draw()
            bottom(x).to.box.up(0.02).draw().down(0.02).text(label, anchor='north')

        for x in self._ticker.minor:
            top(x).to.box.down(0.01).draw()
            bottom(x).to.box.up(0.01).draw()

        return

class VTicks(Layer):
    def __init__(self, ticker):
        Layer.__init__(self)
        self._ticker = ticker

    def draw(self, c):
        left = c.box(0,0).plot.y
        right = c.box(1,0).plot.y


        for y, label in self._ticker.major:
            right(y).to.box.left(0.02).draw()
            left(y).to.box.right(0.02).draw().left(0.02).text(label, anchor='east')

        for y in self._ticker.minor:
            right(y).to.box.left(0.01).draw()
            left(y).to.box.right(0.01).draw()

        return

class HistoData(Layer):
    def __init__(self, data):
        Layer.__init__(self)
        self._data = data

    def draw(self, c):
        _, y0 = c.box(0,0).plot.pos
        x, _, _ = self._data[0]

        c = c.plot(x,y0)

        for x, w, y in self._data:
            c = c.to(x,y).to(x+w, y)

        c = c.to.y(y0)

        c.end.draw(color='red')

h = Histo()
h.fulldraw()
print h._canvas.paint()
