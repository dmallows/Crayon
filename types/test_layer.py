import unittest
from layer import *

class TestPlot(unittest.TestCase):

    def setUp(self):
        self.plot = Plot()

    def test_size(self):
        self.assertEqual(self.plot.size.value, (80, 60))

if __name__=='__main__':
    unittest.main()

