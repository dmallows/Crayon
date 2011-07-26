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
        self._scopes = dict(box = BoxSpace(), paper = paper, absolute=paper)
        self.buffer = [r'\documentclass{article}',
                       r'\usepackage[rgb]{xcolor}',
                       r'\usepackage{tikz}',
                       r'\begin{document}',
                       r'\thispagestyle{empty}',
                       r'\begin{tikzpicture}',
                       r'\definecolor{darkgrey}{rgb}{0.3, 0.3, 0.3}']
        
        self._default = paper

        self._stack = None

    def user_to_device(self, p):
        return p

    def push_path(self, markers, closed=False):
        """Draws a path of markers"""
        buffer = ' -- '.join(
            '(%gmm, %gmm)' % self.user_to_device(m.absolute.pos)
            for m in markers)
        if closed:
            buffer = buffer + ' -- cycle'
        self._stack = buffer

    def cursor(self):
        return Cursor(self, self._scopes, self._default)
    
    def push_circle(self, centre, radius):
        """Draws a circle"""
        x, y = centre.paper._cursor
        self._stack = '(%gmm, %gmm) circle (%gmm)' % (x,y,radius)
    def _tikz_path_command(self, cmd, **kw):
        if kw:
            kw = ', '.join('%s=%s' % (i,j) for i, j in kw.iteritems())
            self.buffer.append(r'\%s [%s] %s ;' % (cmd, kw, self._stack))
        else:
            self.buffer.append(r'\%s %s ;' % (cmd, self._stack))

    def draw(self, **kw):
        self._tikz_path_command('draw', **kw)

    def fill(self, **kw):
        self._tikz_path_command('fill', **kw)

    def filldraw(self, **kw):
        self._tikz_path_command('filldraw', **kw)

    def paint(self):
        #self.buffer.append(r'\end{tikzpicture}')
        return '\n'.join(self.buffer + [r'\end{tikzpicture}',
                                        r'\end{document}'])

    def text(self, pos, label, anchor=None):
        x, y = pos.absolute.pos
        if anchor:
            s = r'\node [anchor=%s] at (%gmm, %gmm) {%s};' % (anchor, x, y, label)
        else:
            s = r'\node at (%gmm, %gmm) {%s};' % (x, y, label)
        self.buffer.append(s)
        return
