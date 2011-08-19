import neat as params
from neat import Int, String, Tuple, Color, Float

class Layer(params.NameSpace):
    def __init__(self, above=None, below=None):
        super(Layer, self).__init__()
        self.above = [] if above is None else above
        self.below = [] if below is None else below

    def add_above(self, v):
        setattr(self, v)
        self.below.append(v)
        return self

    def add_below(self, c):
        setattr(self, v)
        self.above.append(v) 
        return self

class LineStyle(params.NameSpace):
    width = Float()
    color = Color()
    def __init__(self, width = None, height = None):
        super(LineStyle, self).__init__()
        self.width.default = width
        self.width.default = height

class Plot(Layer):
    title  = String('')
    size   = Tuple(Int(default=80), Int(default=60))
    border = LineStyle()
