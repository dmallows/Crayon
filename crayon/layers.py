import crayon.types as types
from crayon.types import Int, String, Tuple, Color, Float

class Layer(types.NameSpace):
    def draw(self, c):
        pass

class LineStyle(types.NameSpace):
    width = Float()
    color = Color()
    def __init__(self, width = None, color = None):
        super(type(self), self).__init__()
        self['width'].default = width
        self['color'].default = color

class DataSet(types.NameSpace):
    linestyle = LineStyle()
    title     = String()

class Plot(Layer):
    title  = String('')
    linestyle = LineStyle()
    size   = Tuple(Int(default=80), Int(default=60))
    border = LineStyle()

    def __init__(self, **kwargs):
        super(Plot, self).__init__()
        for k, v in kwargs.iteritems():
            print k,'=', v

class Histo1D(Plot):
    pass
