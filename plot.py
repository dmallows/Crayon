import math

class Layer(object):
    def __init__(self, above=[], below=[]):
        self._above = above
        self._below = below

    def set(self, above=None, below=None):
        above = above if above is not None else self._above
        below = below if below is not None else self._below
        return Layer(above, below)

    def setup_draw(self, c):
        return c

    def add_above(self, layer):
        return self._above.append(layer)

    def add_below(self, layer):
        return self._below.append(layer)

    def draw(self, c):
        return

    def draw_all(self, c):
        c = self.setup_draw(c)

        for l in reversed(self._below):
            #l.draw_all(c)
            pass

        self.draw(c)

        for l in self._above:
            #l.draw_all(c)
            pass

    def __repr__(self):
        return '( %r %s %r )' % (self._below, self.__class__.__name__, self._above)

class Ticker(object):
    pass

ceil = lambda x : int(math.ceil(x))

class LinTicker(Ticker):
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
        return map(lambda i: (i, self._to_str(i)), ticks)

    def _calc_minor(self, minor, major):
        return []

floor = lambda x: int(math.floor(x))
log = math.log

class LogTicker(Ticker):
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

from context import TikzCanvas
from spaces import LinSpace, LogSpace, Space2D


class Histo(Layer):
    def __init__(self, width=160, height=120):
        Layer.__init__(self)
        self._canvas = TikzCanvas(width, height)

        xspace = LinSpace(0,100)
        yspace = LogSpace(0.001,1000)

        self._space = Space2D(xspace, yspace)

        from numpy import linspace, sin, exp, ones
        x = linspace(0, 99.5, 200)
        y = exp(6.8*sin(x))
        data = zip(x, ones(200)*0.5, y)
        
        self.hticks = HTicks(LinTicker(xspace, 10, 2))
        self.vticks = VTicks(LogTicker(yspace))
        self.data = HistoData(data)

    def setup_draw(self, c):
        # self.set_plot()
        return c

    def draw(self):
        c = self._canvas.cursor()

        c = c.paper(10,10).to.box(1,1).paper.move(-10,-10).zoom()\
                                      .set_plot(self._space)
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
        top = c.box(0,1).plot.right
        bottom = c.box(0,0).plot.right

        for x, label in self._ticker.major:
            top(x).paper.to.down(3).draw()
            bottom(x).paper.to.up(3).draw().down(4).text(label, anchor='north')

        for x in self._ticker.minor:
            top(x).paper.to.up(1.5).draw()
            bottom(x).paper.to.down(1.5).draw()

        return

class VTicks(Layer):
    def __init__(self, ticker):
        Layer.__init__(self)
        self._ticker = ticker

    def draw(self, c):
        left = c.box(0,0).plot.up
        right = c.box(1,0).plot.up

        for y, label in self._ticker.major:
            right(y).to.paper.left(3).draw()
            left(y).paper.to.right(3).draw().left(4).text(label, anchor='east')

        for y in self._ticker.minor:
            right(y).paper.to.left(1.5).draw()
            left(y).paper.to.right(1.5).draw()

        return

class HistoData(Layer):
    def __init__(self, data):
        Layer.__init__(self)
        self._data = data

    def draw(self, c):
        _, y0 = c.box(0,0).plot.pos
        x, _, _ = self._data[0]

        c = c.plot(x,y0)

        for _, w, y in self._data[1:]:
            c = c.to.y(y).to.right(w)

        c.to.y(y0).draw()

h = Histo()
h.fulldraw()
print h._canvas.paint()
