import unittest
import neat 
from neat import *

def ricochet_string(obj, v):
    return obj.to_string(obj.from_string(v))

def ricochet_py(obj, v):
    return obj.to_py(obj.from_py(v))

class TestBool(unittest.TestCase):

    def setUp(self):
        self.b = neat.Boolean()

    def test_bool(self):
        # An Integer should make it fail
        self.assertRaises(ParseError, self.b.from_string, '23')
        # A random string should make it fail
        self.assertRaises(ParseError, self.b.from_string, 'yugga')

    def test_bool_true(self):
        self.assertEqual(True, self.b.from_py(True))

        # The following should all be parsed as True
        for v in ('yes', 'y', 'true', 't'):
            w = v.upper()
            self.assertEqual(True, self.b.from_string(v))
            self.assertEqual(True, self.b.from_string(w))

    def test_bool_false(self):
        self.assertEqual(False, self.b.from_py(False))

        # The following should all be parsed as False
        for v in ('no', 'n', 'false', 'f'):
            w = v.upper()
            self.assertEqual(False, self.b.from_string(v))
            self.assertEqual(False, self.b.from_string(w))

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
            self.assertEquals(ricochet_py(self.enum, s), s.upper())

class TestFloat(unittest.TestCase):

    def setUp(self):
        self.float = neat.Float()

    def test_positives(self):
        for x in xrange(100):
            self.assertEqual(0.1*x, self.float.from_py(0.1*x))

    def test_range(self):
        float = neat.Float(1,5,1)
        for x in xrange(0,10):
            self.assertRaises(TestError, float.from_py, 0.1*x)
        for x in xrange(10,51):
            self.assertEqual(0.1*x, ricochet_py(float, 0.1*x))
        for x in xrange(51, 100):
            self.assertRaises(TestError,float.from_py, 0.1*x)

    def test_range(self):
        float = neat.Float(1,5,1)
        for x in xrange(0,10):
            self.assertRaises(TestError, float.from_py, 0.1*x)
        for x in xrange(10,51):
            self.assertEqual(0.1*x, ricochet_py(float, 0.1*x))
        for x in xrange(51, 100):
            self.assertRaises(TestError,float.from_py, 0.1*x)

class TestFloat(unittest.TestCase):

    def setUp(self):
        self.float = neat.Float()

    def test_positives(self):
        for x in xrange(100):
            self.assertEqual(0.1*x, self.float.from_py(0.1*x))

    def test_range(self):
        float = neat.Float(1,5,1)
        for x in xrange(0,10):
            self.assertRaises(TestError, float.from_py, 0.1*x)
        for x in xrange(10,51):
            self.assertEqual(0.1*x, ricochet_py(float, 0.1*x))
        for x in xrange(51, 100):
            self.assertRaises(TestError,float.from_py, 0.1*x)


class TestMaybe(unittest.TestCase):

    def setUp(self):
        self.maybe = Maybe(Int())
        self.str_maybe = Maybe(String())

    def test_default(self):
        self.assertEquals(self.maybe.default, None)

    def test_set(self):
        self.assertEquals(23, ricochet_py(self.maybe, 23))
        self.assertEquals(None, ricochet_py(self.maybe, None))
        self.assertRaises(ValueError, self.maybe.from_py, 'spud')

    def test_read(self):
        self.assertEquals(23, self.maybe._from_string('23') )
        self.assertRaises(ParseError, self.maybe._from_string, 'goo')

class TestModel(unittest.TestCase):
    def setUp(self):

        class WhatTheFuck(NameSpace):
            lolage = String(default='lol')
        class Parameters(NameSpace):
            label  = String(default='x')
            lol = WhatTheFuck()
            xticks = Maybe(Int())

        self.model = Parameters()
        self.model2 = Parameters()

    def test_params(self):
        self.model.xticks
        self.model.xticks.value = 15
        self.assertEqual(self.model.xticks.value, 15)
        self.model.xticks.value = None 
        self.assertEqual(self.model.xticks.value, None)
        self.model.xticks.value = 15
        self.assertRaises(ValueError, self.model.xticks.set,'lol')
        # As it stands at the *moment*, this will fail. I need to fix this,
        # somehow, but all I can think of is magic.
        self.assertNotEqual(self.model.xticks, self.model2.xticks)

    def test_lookup(self):
        self.assertEqual(self.model.lookup('lol.lolage').value, 'lol')

class Layer(NameSpace):
    def __init__(self):
        super(Layer, self).__init__()
        self.xticks = TickStyle(0, 0.5, '#ffffff')

class TickStyle(NameSpace):
    width  = Float()
    length = Float()
    color  = Color()

    def __init__(self, width=None, length=None, color=None):
        super(TickStyle, self).__init__()
        self.width.default  = lambda: 2 * self.length.value
        self.length.default = length
        self.color.default  = color

class TestLayer(unittest.TestCase):
    def setUp(self):
        self.layer = Layer()

    def test_layer(self):
        self.assertEqual(self.layer.xticks.color.value, '#ffffff')
        self.assertEqual(self.layer.xticks.width.value,
                         2*self.layer.xticks.length.value)

        self.layer.xticks.length.value = 5
        self.assertEqual(self.layer.xticks.width.value,
                         2*self.layer.xticks.length.value)

if __name__ == '__main__':
    unittest.main()
