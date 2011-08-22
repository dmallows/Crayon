import crayon.latex as tex
import contextlib
import unittest

class TestTexRunner(unittest.TestCase):
    def setUp(self):
        self.tex = tex.TexRunner()

    def test_svgs(self):
        texes = self.tex.render(['%05d' % i for i in xrange(10000)])
        print 'Done Tex'
        self.tex.to_svg(texes)
            
    def tearDown(self):
        self.tex.close()

if __name__ == '__main__':
    self.unittest.main()
