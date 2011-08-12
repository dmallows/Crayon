## Defines colour systems and transforms between them.
import colorsys

ident = lambda x: x

_scale = 1.0/255

def rgb_to_rgb255(r,g,b):
    s = 255.0
    return (s*r, s*g, s*b)

def rgb255_to_rgb(r,g,b):
    s = _scale
    return (s*r, s*g, s*b)

class Gradient(obect):
    pass

class LinearGradient(Gradient):
    pass

class ColorSpace(object):
    @property
    def rgb(self):
        raise NotImplementedError()

    def __getattr__(self, attr):
        return getattr(self.rgb, attr)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
                           ', '.join('%g' % r for r in self.color))
    def to(self):
        return self

class Rgb(ColorSpace):
    def __init__(self, r, g, b):
        self.color = r, g, b
    @property
    def rgb(self):
        return self

    @property
    def hsv(self):
        return Hsv(*colorsys.rgb_to_hsv(*self.color))

    @property
    def rgb255(self):
        return Rgb255(*rgb_to_rgb255(*self.color))


class Hsv(ColorSpace):
    def __init__(self, hue, sat, val):
        self.color = hue, sat, val

    @property
    def rgb(self):
        return Rgb(*colorsys.hsv_to_rgb(*self.color))

    @property
    def hsv(self):
        return self

class Rgb255(ColorSpace):
    _scale = 1.0/255
    def __init__(self, r, g, b):
        self.color = r, g, b

    @property
    def rgb(self):
        return Rgb(*rgb255_to_rgb(*self.color))

    @property
    def rgb255(self):
        return self

    @property
    def hex(self):
        return '#%02x%02x%02x' % self.color

class Hex(Rgb255):
    def __init__(self, text):
        t = text.strip('#')
        if len(t) == 6:
            split = t[0:2], t[2:4], t[4:6]
        elif len(t) == 3:
            split = (i*2 for i in t)
        else:
            raise ValueError('Unable to parse hex string')

        r, g, b = (int(i, 16) for i in split)
        Rgb255.__init__(self, r,g,b)
