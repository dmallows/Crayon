import unittest
import neat 
from neat import *

class TestBool(unittest.TestCase):

    def setUp(self):
        self.b = neat.Boolean()

    def test_bool(self):
        # An Integer should make it fail
        self.assertRaises(ParseError, self.b.read, '23')
        # A random string should make it fail
        self.assertRaises(ParseError, self.b.read, 'yugga')

    def test_bool_true(self):
        self.assertEqual(True, self.b.set(True).get())

        # The following should all be parsed as True
        for v in ('yes', 'y', 'true', 't'):
            w = v.upper()
            self.assertEqual(True, self.b.read(v).get())
            self.assertEqual(True, self.b.read(w).get())

    def test_bool_false(self):
        self.assertEqual(False, self.b.set(False).get())

        # The following should all be parsed as False
        for v in ('no', 'n', 'false', 'f'):
            w = v.upper()
            self.assertEqual(False, self.b.read(v).get())
            self.assertEqual(False, self.b.read(w).get())

class TestString(unittest.TestCase):

    def setUp(self):
        self.b = neat.String()

    def test_string(self):
        # No heroics - we want the string to just be settable to strings!
        self.assertRaises(TestError, self.b.set, True)
        self.assertRaises(TestError, self.b.set, 18)
        self.assertRaises(TestError, self.b.set, 63.2333333)

    def test_string(self):
        # No heroics - we want the string to just be settable to strings!
        self.b.value = 'hello'
        self.assertEqual(self.b.value, 'hello')

class TestEnum(unittest.TestCase):

    def setUp(self):
        self.strings = ('foo', 'bar', 'baz')
        self.enum = neat.Enum(self.strings)

    def test_positives(self):
        for s in self.strings:
            self.enum.set(s.upper())

class TestInt(unittest.TestCase):

    def setUp(self):
        self.int = neat.Int()

    def test_positives(self):
        for x in xrange(100):
            self.assertEqual(x, self.int.set(x).get())

    def test_range(self):
        int = neat.Int(10,50,10)
        for x in xrange(0,10):
            self.assertRaises(TestError, int.set, x)
        for x in xrange(10,51):
            self.assertEqual(x, int.set(x).get())
        for x in xrange(51, 100):
            self.assertRaises(TestError, int.set, x)

class TestFloat(unittest.TestCase):

    def setUp(self):
        self.float = neat.Float()

    def test_positives(self):
        for x in xrange(100):
            self.assertEqual(0.1*x, self.float.set(0.1*x).get())

    def test_range(self):
        float = neat.Float(1,5,1)
        for x in xrange(0,10):
            self.assertRaises(TestError, float.set, 0.1*x)
        for x in xrange(10,51):
            self.assertEqual(0.1*x, float.set(0.1*x).get())
        for x in xrange(51, 100):
            self.assertRaises(TestError, float.set, 0.1*x)

class TestMaybe(unittest.TestCase):

    def setUp(self):
        self.maybe = Maybe(Int())
        self.str_maybe = Maybe(String())

    def test_default(self):
        self.assertEquals(self.maybe.get(), None)

    def test_set(self):
        self.assertEquals(23, self.maybe.set(23).get())
        self.assertEquals(None, self.maybe.set(None).get())
        self.assertRaises(ValueError, self.maybe.set, 'spud')

    def test_set_str(self):
        self.assertEquals('23', self.str_maybe.set('23').get())
        self.assertEquals(None, self.str_maybe.set(None).get())
        self.assertRaises(TestError, self.str_maybe.set, 11)

    def test_read(self):
        self.assertEquals(23, self.maybe.read('23').get())
        self.assertRaises(ParseError, self.maybe.read, 'goo')

class TestModel(unittest.TestCase):
    def setUp(self):
        class MyModel(Model):
            label  = String(default='x')
            xticks = Maybe(Int())

        self.model = MyModel()

    def test_params(self):
        print self.model.xticks
        self.model.xticks = 15
        print self.model.xticks

if __name__ == '__main__':
    unittest.main()

