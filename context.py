from collections import deque
from exceptions import RuntimeError
#import numpy as np
from math import sqrt, log
#import cairo

from point import Cursor
from spaces import LinSpace, Space2D, BoxSpace, LogSpace
##from affine import Affine2D

class TikzCanvas(object):
    """Low-level stateful graphics context"""
    def __init__(self, width, height):
        paper = Space2D(LinSpace(0,width),LinSpace(0, height))
        plot = Space2D(LinSpace(0, 100), LogSpace(10,1000))
        self._scopes = dict(box = BoxSpace(), paper = paper, absolute=paper,
                            plot = plot) # Simplest space

        self.buffer = []
        self.buffer.append(r'\begin{tikzpicture}')
        
        self._default = paper

        self._stack = None

    def user_to_device(self, p):
        return p

    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        buffer = ' -- '.join('(%gmm, %gmm)' % self.user_to_device(m.pos) for m in markers)
        if closed:
            buffer = buffer + ' -- cycle'
        self._stack = buffer

    def cursor(self):
        return Cursor(gc, self._scopes, self._default)
    
    def push_circle(self, centre, radius):
        """Draws a circle"""
        x, y = centre.paper._cursor
        self._stack = '(%gmm, %gmm) circle (%gmm)' % (x,y,radius)

    def draw(self):
        self.buffer.append(r'\draw %s ;' % self._stack)

    def fill(self):
        self.buffer.append(r'\fill %s ;' % self._stack)

    def filldraw(self):
        self.buffer.append(r'\filldraw %s ;' % self._stack)

    def paint(self):
        #self.buffer.append(r'\end{tikzpicture}')
        print '\n'.join(self.buffer + [r'\end{tikzpicture}'])

    def set_plot(self, plot):
        self._scopes['plot'] = plot

    def set_local(self, local):
        self._scopes['local'] = local

    def set_global(self, glob):
        self._scopes['global'] = glob

gc = TikzCanvas(80,60)
c = gc.cursor()

d = c.box(0.1,0.1).to(0.9,0.9).zoom()

if __name__=='__main__':
    c.to.box(1,1).rect.draw()
    c.to.right(10).circle().draw()
    print c._gc.buffer
    gc.paint()

