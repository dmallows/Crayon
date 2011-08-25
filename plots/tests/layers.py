import unittest
import plots.layers as layers

import crayon.contexts.cairo as cc
from crayon.latex import TexRunner
import cairo
from contextlib import closing

class TestPlot(unittest.TestCase):

    def setUp(self):
        self.plot = layers.Plot()

    def test_size(self):
        self.plot.size = 90, 40
        self.assertEqual(self.plot.size, (90, 40))
        self.assertEqual(self.plot['size'].value, (90, 40))

        del self.plot.size
        self.assertEqual(self.plot.size, (80, 60))


    def test_style(self):
        self.plot.linestyle['width'].default = 10
        self.assertEqual(self.plot.linestyle.width, 10)


class TestHisto(unittest.TestCase):
    def setUp(self):
        self.histo = layers.Histo1D(title='My Pretty Plot')

    def test_something(self):
        tr = TexRunner()
        c = cairo.PDFSurface('outputs/cairo-out.pdf',
                             *(cc.MM2PT*x for x in (80,60)))
        
        canvas = cc.CairoCanvas(cairo.Context(c), tr, 80, 60)
        
        self.histo.draw(canvas.cursor())
        c.finish()

if __name__=='__main__':
    unittest.main()
