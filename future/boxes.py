#! /usr/bin/python
# This will be interesting

# We need an unset class for

"""class Margin(NameSpace):
    left = Float(default=0.0)
    right = Float(default=0.0)
    bottom = Float(default=0.0)
    top = Float(default=0.0)

"""

class Box(object):
    def __init__(self, title, size, expand=False):
        self.title = title
        self.size = None
        self.expand = expand
    def __repr__(self):
        return 'B(%s)' % self.title

xlabel = Box('xlabel', (50.0, 10.0))
xticks = Box('xticks', (50.0, 10.0))
ylabel = Box('ylabel', (10.0, 50.0))
yticks = Box('yticks', (10.0, 50.0))
title = Box('title',  (10.0, 50.0))
data = Box('data', (50.0, 50.0), True)

class Group(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        return 'Group({0}, {1})'.format(', '.join(str(i) for i in self._args), self._kwargs)

    def __iter__(self):
        return self._args.__iter__()
    

xlayout = [[ylabel], [yticks], [title, data, xticks, xlabel]]
ylayout = [[title], [ylabel, yticks, data], [xlabel], [xticks]]

layout = {}
pointset = set()

# Create numerical references for box
for xi, xs in enumerate(xlayout):
    for x in xs:
        for yi, ys in enumerate(ylayout):
            for y in ys:
                if y is x:
                    p = xi, yi
                    if p in pointset:
                        raise KeyError('Items clash for same space')
                    layout.setdefault(x, []).append((xi, yi))
                    pointset.add(p)

for box, points in layout.iteritems():
    x1, y1 = min(points)
    x2, y2 = max(points)
    nx, ny = 1+x2-x1, 1+y2-y1
    if nx*ny != len(points):
        raise ValueError('%r is not laid out as a rectangle' % box)
    layout[box] = (x1, y1, nx, ny)

#Calculate horizontal positions subject to constraints...

