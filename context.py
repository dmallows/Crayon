from collections import deque
from exceptions import RuntimeError
#import numpy as np
from math import sqrt, log
#import cairo

from point import Cursor
from spaces import LinSpace, Space2D

class TikzContext(object):
    """Low-level stateful graphics context"""
    def __init__(self, width=80, height=60):
        self.size = width, height

        self._paper = Space2D(LinSpace(0,width),LinSpace(0, height))
        self._plot = None 

        self.buffer = []
        self.buffer.append(r'\begin{tikzpicture}')

        self._stack = None

    def user_to_device(self, point):
        """Converts from userspace to device space"""
        return point
   
    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        buffer = ' -- '.join('(%gmm, %gmm)' % self.user_to_device(m.pos) for m in markers)
        if closed:
            buffer = buffer + ' -- cycle'
        self._stack = buffer

    def cursor(self):
        return Cursor(gc, self._paper, self._plot)
    
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
        self._plot = plot

gc = TikzContext(80,60)
c = gc.cursor()

if __name__=='__main__':
    c.box.to(1,1).rect().filldraw()
    c.to.right(10).circle().draw()
    print c._gc.buffer
    gc.paint()
