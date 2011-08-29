import unittest
from cursor import Cursor
import cPickle

class TestAngle(unittest.TestCase):
    pass

class TestCursor(unittest.TestCase):
    def test_move(self):
        """Check that we can draw a 10 x 10 square and return at our
        starting position"""
        c = Cursor(0,0)
        c.move(10,0)
        self.assertEqual((10, 0), c.pos)
        c.move(0,10)
        self.assertEqual((10, 10), c.pos)
        c.move(-10,0)
        self.assertEqual((0, 10), c.pos)
        c.move(0, -10)
        self.assertEqual((0, 0), c.pos)

    def test_compass(self):
        c = Cursor(0,0).to.N(10).to.E(10).to.S(10).to
        self.assertEqual(c._path, [(0,0), (0,10), (10,10), (10,0)])
        c = Cursor(0,0).to.NW(10).to.NE(10).to.SE(10).to
        c2 = Cursor(0,0).to.NE(10)
        self.assertEqual(c.pos, c2.pos)

    def test_copy(self):
        c = Cursor(10, 10)
        c2 = c.clone
        c2.move(-10, -10)
        self.assertEqual(c2.pos, (0,0))
        self.assertNotEqual(c2.pos, c.pos)

    def test_to(self):
        c = Cursor(0,0)
        self.assertEqual(c.to(10,10).to._path, [(0,0), (10,10)])

    def test_pickle(self):
        c = Cursor(0,0).NW(10)
        c2 = cPickle.loads(cPickle.dumps(c))
        self.assertEqual(c.pos, c2.pos)

    def test_angle(self):
        c = Cursor(0,0).to.NW(10).angle
        print c


    def test_bearing(self):
        c = Cursor(0,0)
        self.assertEqual(0, c(0,0).to.N(10).angle)
        self.assertEqual(90, c(0,0).to.E(10).angle)
        self.assertEqual(180, c(0,0).S(10).angle)
        self.assertEqual(270, c(0,0).to.W(10).angle)
        
        for x in (11.8, 279.15, 87.3, 100.2):
            self.assertAlmostEqual(x, c(0,0).head(x).angle)

if __name__=='__main__':
    unittest.main()
