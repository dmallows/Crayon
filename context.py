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

class Context(object):
    """Low-level stateful graphics context"""
    def user_to_device(self, point):
        """Converts from userspace to device space"""
        pass
    
    def rectangle(self, a, b):
        """Draw a rectangle from cursor a to cursor b"""
        pass

    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        pass
    
    def push_circle(self, centre, radius):
        """Draws a path of markers"""
        x, y = centre.paper._cursor
        print "Circle<%r %r %r>" % (x, y, radius)

    
