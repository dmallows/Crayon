from typesys import Int, String, Tuple, Color, Float, NameSpace, Maybe
from crayon.spaces import LinSpace, LogSpace, Space2D

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

class Layer(NameSpace):
    def __init__(self):
        super(Layer, self).__init__()

    def draw(self, c):
        pass

class LineStyle(NameSpace):
    width = Float()
    color = Color()
    fill  = Maybe(Color())
    def __init__(self, width = None, color = None):
        super(type(self), self).__init__()
        self['width'].default = width
        self['color'].default = color

class DataSet(NameSpace):
    linestyle = LineStyle()
    title     = Maybe(String())

class Plot(Layer):
    title  = String('')
    linestyle = LineStyle()
    size   = Tuple(Int(default=80), Int(default=60))
    border = LineStyle()

    def __init__(self, **kwargs):
        super(Plot, self).__init__()
        for k, v in kwargs.iteritems():
            print k,'=', v

    def draw(self, c):
        c = c.set_plot(Space2D(self.x.space, self.y.space))
        for d in self._drawall:
            d.draw(c)


# Methinks we can abstract yet more away!
class TickLayer(Layer):

    major_length = Float(default=1.5)
    minor_length = Float(default=1.0)
    text_separation = Float(default=1.0)

    def __init__(self, ticker):
        super(TickLayer, self).__init__()
        self.set_ticker(ticker)

    def set_ticker(self, ticker):
        self._ticker = ticker
        return self


class HTicks(TickLayer):


    def draw(self, c):
        top = c.box(0,1).plot.x
        bottom = c.box(0,0).plot.x

        dmaj = self.major_length
        dmin = self.minor_length
        tback = self.text_separation + dmaj

        for x in self._ticker.minor:
            top(x).to.paper.down(dmin).draw()
            bottom(x).to.paper.up(dmin).draw()

        for x, label in self._ticker.major:
            top(x).to.paper.down(dmaj).draw()
            b = bottom(x).to.paper.up(dmaj).draw()
            b.down(tback).text(label, anchor='north')

        return self


class VTicks(TickLayer):

    def draw(self, c):
        left = c.box(0,0).plot.y
        right = c.box(1,0).plot.y

        dmaj = self.major_length
        dmin = self.minor_length
        tback = self.text_separation + dmaj

        for y in self._ticker.minor:
            left(y).to.paper.right(dmin).draw()
            right(y).to.paper.left(dmin).draw()

        for y, label in self._ticker.major:
            right(y).to.paper.left(dmaj).draw()
            l = left(y).to.paper.right(dmaj).draw()
            l.left(tback).text(label, anchor='east')

        return self

class HistoData1D(DataSet):

    def set_data(self, data):
        self._data = data
        return self

    def draw(self, c):
        _, y0 = c.box(0,0).plot.pos
        x, _, _ = self._data[0]

        c = c.plot(x,y0)

        for x, w, y in self._data:
            c = c.to(x,y).to(x+w, y)

        c = c.to.y(y0)

        c.draw(color='red')

class Frame(Layer):
    linestyle = LineStyle()
    def draw(self, c):
        c.box(0,0).to(1,1).rect.draw()

class Histo1D(Plot):
    x = NameSpace()
    y = NameSpace()

    def __init__(self, **kwargs):
        # We have to get kwargs out...
        super(Histo1D, self).__init__(**kwargs)

        x, y = self.x, self.y

        x.space = LinSpace(0, 100)
        y.space = LogSpace(0.001, 1000)

        x.ticker = LinTicker(x.space, 20, 1)
        x.ticks = HTicks(x.ticker)

        y.ticker = LogTicker(y.space)
        y.ticks = VTicks(y.ticker)

        self.data = HistoData1D().set_data([(0,50,1),(50,50,10)])

        self.frame = Frame()

        self._drawall = [self.frame, self.x.ticks, self.y.ticks, self.data]

    def draw(self, c):
        c = c(10,5).to(75,55).zoom()
        super(Histo1D, self).draw(c)
