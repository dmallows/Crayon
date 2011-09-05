import unittest
import cursor
import cPickle
import sys
from os.path import abspath

sys.path.append(abspath('..'))

from crayon.spaces import Space2D, LinSpace2D, BoxSpace

class MockContext(object):
    def __getattr__(self, attr):
        return self
    def __call__(self, *args):
        return self

class TestCursor(unittest.TestCase):
    def setUp(self):
        spaces = {'paper':LinSpace2D(0,0,80,60),
                  'absolute':LinSpace2D(0,0,800,600),
                  'box':BoxSpace()}
        self.c = cursor.Cursor(MockContext(), spaces, spaces['paper'] )

    def test_move(self):
        """Check that we can draw a 10 x 10 square and return at our
        starting position"""
        c = self.c

        c.move(10,0)
        self.assertEqual((10, 0), c.pos)
        c.move(0,10)
        self.assertEqual((10, 10), c.pos)
        c.move(-10,0)
        self.assertEqual((0, 10), c.pos)
        c.move(0, -10)
        self.assertEqual((0, 0), c.pos)

    def test_compass(self):
        c = self.c.copy()

        c = c(0,0).to.N(10).to.E(10).to.S(10).to
        self.assertEqual(c._path, [(0,0), (0,10), (10,10), (10,0)])

        c = self.c.copy()
        c(0,0).to.NW(10).to.NE(10).to.SE(10).to

        c2 = self.c.copy()
        c2(0,0).to.NE(10)

        self.assertEqual(c.pos, c2.pos)

    def test_copy(self):
        c = self.c
        c(10, 10)

        c2 = c.copy()
        c2.move(-10, -10)

        self.assertEqual(c2.pos, (0,0))
        self.assertNotEqual(c2.pos, c.pos)

    def test_to(self):
        c = self.c
        c(0,0)
        self.assertEqual(c.to(10,10).to._path, [(0,0), (10,10)])

    def test_pickle(self):
        c = self.c.copy()
        c = c(0,0).NW(10)
        c2 = cPickle.loads(cPickle.dumps(c))
        self.assertEqual(c.pos, c2.pos)

    def test_angle(self):
        c = self.c
        c(0,0).to.NW(10)
        self.assertAlmostEqual(315, c.degrees)

    def test_bearing(self):
        c = self.c

        self.assertEqual(0, c(0,0).to.N(10).degrees)
        self.assertEqual(90, c(0,0).to.E(10).degrees)
        self.assertEqual(180, c(0,0).S(10).degrees)
        self.assertEqual(270, c(0,0).to.W(10).degrees)
        
        for x in (11.8, 279.15, 87.3, 100.2):
            self.assertAlmostEqual(x, c(0,0).bearing(x).degrees)

    def test_spaces(self):
        self.assertEquals(self.c(40,30).box.pos, (0.5,0.5))
        self.assertEquals(self.c(0, 0).box.pos, (0,0))
        self.assertEquals(self.c.box(1, 1).paper.pos, (80,60))

    def test_item(self):
        c = self.c.copy()
        c(10,10)
        paper = c['paper']
        c['paper'] = c['absolute']

        x, y = c.pos
        self.assertAlmostEquals(x, 100)
        self.assertAlmostEquals(y, 100)

        c['paper'] = paper
        x, y = c.pos
        self.assertAlmostEquals(x, 10)
        self.assertAlmostEquals(y, 10)

    def test_subclassing(self):
        class CursorDeluxe(cursor.Cursor):
            plot = cursor.ChangeView('plot')
        
        c = self.c.copy(CursorDeluxe)
        c['plot'] = LinSpace2D(50,50,100,100)
        
        self.assertAlmostEqual(
            c.box(1,1).plot.pos, (100,100))

        self.assertAlmostEqual(
            c.box(0,0).plot.pos, (50,50))

    def test_zoom(self):
        c = self.c
        c.paper(0,0).to(10,10).zoom()
        x, y = c.box(1,1).paper.pos
        self.assertAlmostEquals(x, 10)
        self.assertAlmostEquals(y, 10)

        x, y = c.box(1,1).absolute.pos
        self.assertAlmostEquals(x, 100)
        self.assertAlmostEquals(y, 100)

    def test_paths(self):
        c = self.c
        c(0,0).to(1,0).to(1,1).to(1,0).curve

if __name__=='__main__':
    unittest.main()
