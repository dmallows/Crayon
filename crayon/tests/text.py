import unittest

import crayon.contexts.cairo as cc
from crayon.latex import TexRunner
import cairo
from contextlib import closing

class TestText(unittest.TestCase):
    def test_something(self):
        with closing(TexRunner()) as tr:
            cs = cairo.PDFSurface('outputs/cairo-out.pdf',
                                  *map(lambda x: cc.MM2PT * x, (80,60)))
            
            canvas = cc.CairoCanvas(cairo.Context(cs), tr, 80, 60)
            c = canvas.cursor()
            c(50,20).text(r'1 2 3 4 5 6 7 8 9 0',
                          anchor='east')
            
            cs.finish()

if __name__=='__main__':
    unittest.main()
