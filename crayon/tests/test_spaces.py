import bijection
import unittest

class TestBijectionFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_log_bijection(self):
        f,g = bijection.create_log_bijection(10,1000)
        self.assertAlmostEqual(f(g(100)), 100)
        self.assertAlmostEqual(f(g(10)), 10)
        self.assertAlmostEqual(f(g(1)), 1) 
        self.assertAlmostEqual(f(100), 0.5) 

    def test_lin_bijection(self):
        f,g = bijection.create_lin_bijection(0,1000)
        self.assertAlmostEqual(f(g(100)), 100)
        self.assertAlmostEqual(f(g(10)), 10)
        self.assertAlmostEqual(f(g(1)), 1) 
        self.assertAlmostEqual(f(500), 0.5) 
