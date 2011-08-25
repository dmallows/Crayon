import crayon.latex as latex
import contextlib
import unittest
import shutil
import os

class TestTexRunner(unittest.TestCase):
    def setUp(self):
        pass


    def test_svgs(self):
        tex = latex.TexRunner()
        texes = tex.render(['%04d' % i for i in xrange(1010)])
        # print texes
        texes = tex.to_svg(texes)
        for t in texes:
            print t.svgfile

        tex.close()

    def tearDown(self):
        #self.tex.close()
        #shutil.rmtree(os.path.expanduser('~/.cache/crayon'))
        pass

if __name__ == '__main__':
    unittest.main()
