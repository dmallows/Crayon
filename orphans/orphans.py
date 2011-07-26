class Coordinates(object):
    def translate(self, dx, dy):
        # Translate by dx, dy.
        return self.transform(lambda x,y: (x+dx, y+dy))

    def transform(self, f):
        return Coordinates(self._transforms + (f,))

    def scale(self, sx, sy):
        # Scale by sx, sy
        return self.transform(lambda x, y: (x*sx, y*sy))

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
