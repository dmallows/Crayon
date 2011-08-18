# The stuff going on here... well, think of these Params as towers.
# As a parameter is parsed, 
# Look to Django ORM for where the ideas came from!
# The rest of the madness is mine.

## Candidates for moving to an exception module

## FUCK THE NONETYPES!
## THEY ARE CAUSING ALL OUR PROBLEMS.
## AND THEY MAY NEVER BE NEEDED!!!
## AT LEAST FOR MANY THINGS.

class Error(Exception):
    def __str__(self):
        return '%r: %s' % (self.expr, self.msg)

class ParseError(Error):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class TestError(Error):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
    def __str__(self):
        return '%s: %s' % (self.expr.__class__.__name__, self.msg)

class Param(object):
    # Counter for ordering
    _counter = 0
    def __init__(self, tests = ()):
        self._counter = Param._counter
        Param._counter += 1
        self._tests = tests
    
    def read(self, v):
        return self._set(self._from_str(v))

    def show(self):
        return self._to_str(self._get())

    def get(self):
        return self._to_py(self._get())

    def set(self, v):
        return self._set(self._from_py(v))

    def _from_py(self, v):
        return v

    def _to_py(self, v):
        return v

    def _get(self):
        return self._value

    def _set(self, v):
        for e in (TestError(f, v) for f in self._tests if f(v) is False):
            raise e

        self._value = v

        return self

    def __get__(self, obj, type=None):
        return self.get()
    def __set__(self, obj, v):
        self.set(v)
        
## Lambdas have known problems when it comes to pickling. Classes are more
## solid. Here are some classes!

class RangeTest(object):
    def __init__(self, a, b):
        self._r = a, b
    def __call__(self, v):
        if v is None:
            return True
        a, b = self._r
        return (v >= a and v <= b)

class ElementTest(object):
    def __init__(self, *ps):
        self._ps = ps
    def __call__(self, v):
        return (v in self._ps)

class ShallowElementTest(object):
    def __init__(self, *ps):
        self._ps = ps
    def __call__(self, v):
        for p in self._ps:
            if p is v:
                return True
        return False

class DeepElementTest(object):
    def __init__(self, *ps):
        self._ps = ps
    def __call__(self, v):
        for p in self._ps:
            if p == v:
                return True
        return False

class InstanceTest(object):
    def __init__(self, cls):
        self._cls = cls
    def __call__(self, v):
        return isinstance(v, self._cls)

## How?
class Maybe(Param):
    def __init__(self, proxy, default = None):
        super(Maybe, self).__init__()
        self._proxy = proxy
        self.set(default)

    def _from_py(self, v):
        # Maybe swallows the value if it's None
        if v is None:
            return
        else:
            return self._proxy.set(v)

    def _to_py(self, v):
        try:
            return v.get()
        except AttributeError:
            return

    def _from_str(self, s):
        if s is '':
            return
        else:
            return self._proxy.read(s)

    def _to_str(self, v):
        if v is None:
            return ''
        else:
            return v.show()

class Boolean(Param):
    def __init__(self, default=False):
        Param.__init__(self, tests=(ElementTest(True, False),))
        self.set(default)

    def _to_str(self):
        return repr(self.get())

    def _from_str(self, v):
        v = v.strip().lower()
        if v in ('true','t','yes','y','1'):
            return True
        elif v in ('false','f','no','n','0'):
            return False
        else:
            raise ParseError(v,"Couldn't parse")

class String(Param):
    def __init__(self, default=None):
        Param.__init__(self, tests=(InstanceTest(basestring),))

    def _from_str(self, v):
        return v

    def _to_str(self):
        return self.get()


class Enum(Param):
    def __init__(self, vals, default = None):
        vals = tuple(v.upper() for v in vals)
        default = vals[0] if default is None else default
        
        super(Enum, self).__init__(tests = (ElementTest(*vals),))
        self.set(default)

    def _from_py(self, v):
        return v.upper()
    
    def _from_txt(self, v):
        return v.upper()

    def _to_txt(self, v):
        return v.upper()


class Number(Param):
    def __init__(self, min=None, max=None, default=0):
        tests = ()
        if max is not None or min is not None:
            tests = (RangeTest(min, max),)

        Param.__init__(self, tests=tests)

        self.set(default)

class Int(Number):
    def show(self):
        v = self.get()
        return '%d' % v if v is not None else ''

    def _from_py(self, v):
        try:
            return int(v)
        except ValueError:
            raise

    def _from_str(self, v):
        try:
            return int(v)
        except ValueError as e:
            raise ParseError(v, str(e))

class Float(Number):
    def _to_str(self, v):
        return '%g' % v

    def _from_str(self, v):
        return float(v)

    def _from_py(self, v):
        return float(v)

from collections import OrderedDict

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        params = [(name, attrs.pop(name)) for name, obj in attrs.items() if
                  isinstance(obj, Param)]
        attrs = dict(attrs.items() + params)
        new_class = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        return new_class

class Model(object):
    __metaclass__ = ModelMeta

a = Boolean()
