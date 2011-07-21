from collections import deque
from exceptions import RuntimeError
#import numpy as np
from math import sqrt, log
#import cairo

class Pen(object):
    def __init__(self, color=(0,0,0), linewidth=1):
        self.color = color
        self.linewidth = linewidth

    def set_rgb(self, r,g,b):
        """Set the current colour"""
        self.color = (r, g, b)

    def set_linewidth(self, linewidth):
        """Set the current linewidth"""
        self.linewidth = linewidth

class TikzContext(object):
    """Low-level stateful graphics context"""
    def __init__(self, width=80, height=60):
        self.size = width, height

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
        self.buffer.append(r'\end{tikzpicture}')
        print '\n'.join(self.buffer)
