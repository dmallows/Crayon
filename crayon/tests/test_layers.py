import unittest
import crayon.layers as layers

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
        self.histo

if __name__=='__main__':
    unittest.main()

