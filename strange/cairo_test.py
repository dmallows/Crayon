#!/usr/bin/env python

import math
import cairo
#from crayon.contexts.cairo import CairoContext

scale = 72.0 / 25.4
WIDTH, HEIGHT = 80*scale, 60 * scale

ctx = cairo.Context (surface)
ctx.scale (scale, scale) # Normalizing the canvas

ctx.set_line_width(0.5/scale)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

ctx.rectangle (2, 2, 76, 56) # Rectangle(x0, y0, x1, y1)
ctx.stroke ()

surface.finish() 


surface = cairo.PDFSurface ('output.pdf', WIDTH, HEIGHT)

