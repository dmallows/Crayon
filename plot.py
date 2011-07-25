import math

class Layer(object):
    def __init__(self, above=(), below=()):
        self._above = above
        self._below = below

    def set(self, above=None, below=None):
        above = above if above is not None else self._above
        below = below if below is not None else self._below
        print above, below
        return Layer(above, below)

    def add_above(self, layer):
        return self._above.append(layer)

    def add_below(self, layer):
        return self._below.append(layer)

    def draw(self, c):
        raise NotImplementedError()

    def draw_all(self, c):
        for l in reversed(self._below):
            l.draw_all(c)

        self.draw(c)

        for l in self._above:
            l.draw_all(c)
    
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
        return None

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
        return [(10**i, self._to_str(i)) for i in xrange(a, b+1)]

    def _calc_minor(self):
        # Concat lists together
        lsum = lambda xs: reduce(lambda x, y: x + y, xs)

        return lsum([0.1*i*x for i in xrange(2,10)] for x,_ in self.major[1:])

class Plot(Layer):
    def __init__(self):
        pass

class HTicks(Layer):
    def __init__(self, ticker):
        self._ticker = ticker

    def draw(self, c):
        top = c.box(0,1).plot.right
        bottom = c.box(0,0).plot.right

        for x, label in self._ticker.major:
            top(x).paper.to.down(5).draw()
            bottom(x).paper.to.up(5).draw().down(10).text(label, anchor='N')

        for x in self._ticker.minor:
            top(x).paper.to.up(3).draw()
            bottom(x).paper.to.down(3).draw()

class VTicks(Layer):
    def __init__(self, ticker):
        self._ticker = ticker

    def draw(self, c):
        left = c.box(0,0).plot.up
        right = c.box(1,0).plot.up

        for y, label in self._ticker.major:
            right(y).paper.to.left(5).draw()
            left(y).paper.to.right(5).draw().left(10).text(label, anchor='E')

        for y in self._ticker.minor:
            right(y).paper.to.left(5).draw()
            left(y).paper.to.right(3).draw()

class Data(Layer):
    pass

from spaces import LinSpace, LogSpace

s = LogSpace(0.0001,10000)
t = LogTicker(s)
