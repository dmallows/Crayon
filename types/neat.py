# The stuff going on here... well, think of these Params as things that convert
# between data types. Something like that.
# Look to Django ORM for where (some of) the ideas came from!
# The rest of the madness is probably mine.

# Disclaimer:
# Abandon all hope, ye who enter here.

## Candidates for moving to an exception module

## FECK! NONES!

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
    def __init__(self, test = None, default = None):
        self._counter = Param._counter
        Param._counter += 1
        self._test = test
        self._default = default
    
    # The whole defaults thing is a *little* weird. Defaults are *optional* and
    # totally unchecked at this level! This allows for them to be reset later in
    # Value.

    @property
    def default(self):
        return self._default
    
    def from_py(self, v):
        return self.test(self._from_py(v))

    def _from_py(self, v):
        return v

    def to_py(self, v):
        return self._to_py(v)

    def _to_py(self, v):
        return v

    def from_string(self, v):
        return self.test(self._from_string(v))

    def to_string(self, v):
        return self._to_string(v)

    def test(self, v):
        f = self._test
        if f:
            f(v)
        return v
        
## Lambdas have known problems when it comes to pickling. Classes are more
## solid. Here are some classes!

class RangeTest(object):
    def __init__(self, min, max):
        self._r = min, max

    def __call__(self, v):
        if v is None:
            return True

        result = True

        a, b = self._r

        if a is not None:
            if v < a:
                raise TestError(self, '%s < %s' % (v,a))

        if b is not None:
            if v > b:
                raise TestError(self, '%s > %s' % (v,b))

        return v 

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

    def _from_py(self, v):
        # Maybe swallows the value if it's None
        if v is None:
            return
        else:
            return self._proxy.from_py(v)

    def _to_py(self, v):
        if v is None:
            return None
        else:
            return self._proxy.to_py(v)

    def _from_string(self, s):
        if s is '':
            return
        else:
            return self._proxy.from_string(s)

    def _to_string(self, v):
        if v is None:
            return ''
        else:
            return self._proxy.to_string(v)

class Boolean(Param):
    def __init__(self, default=False):
        Param.__init__(self, test=ElementTest(True, False), default=default)

    def to_string(self, v):
        return repr(self.get())

    def _from_string(self, v):
        v = v.strip().lower()
        if v in ('true','t','yes','y','1'):
            return True
        elif v in ('false','f','no','n','0'):
            return False
        else:
            raise ParseError(v,"Couldn't parse")

class String(Param):
    def __init__(self, default=None):
        Param.__init__(self, test=InstanceTest(basestring), default=default)

    def _from_string(self, v):
        return v

    def to_string(self, v):
        return v

class Enum(Param):
    def __init__(self, vals, default = None):
        vals = tuple(v.upper() for v in vals)
        default = vals[0] if default is None else default.upper()
        assert(default in vals)
        
        super(Enum, self).__init__(test = ElementTest(*vals), default=default)

    def _from_py(self, v):
        return v.upper()
    
    def _from_string(self, v):
        return v.upper()

    def _to_string(self, v):
        return v.upper()

class Number(Param):
    def __init__(self, min=None, max=None, default=0):
        super(Number, self).__init__(test=RangeTest(min, max), default=default)

class Int(Number):
    def show(self):
        v = self.get()
        return '%d' % v if v is not None else ''

    def from_py(self, v):
        try:
            return int(v)
        except ValueError:
            raise

    def _from_string(self, v):
        try:
            return int(v)
        except ValueError as e:
            raise ParseError(v, str(e))

    def _to_string(self, v):
        return '%d' % v

class Float(Number):
    def _to_str(self, v):
        return '%g' % v

    def _from_str(self, v):
        return float(v)

    def _from_py(self, v):
        return float(v)

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
        params = ((name, attrs.pop(name)) for name, obj in attrs.items() if
                  isinstance(obj, Param))
        attrs['_params'] = OrderedDict(params)
        new_class = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        return new_class

class Value(object):
    def __init__(self, param, default=None):
        self._param = param
        self.default = param.default
        self._value = None

    def get(self):
        value = self.default if self._value is None else self._value
        return self._param.to_py(value)

    def set(self, v):
        self._value = self._param.from_py(v)

    @property
    def changed(self):
        return self._value is not None

    value = property(get, set)

    def show(self):
        return self._param.to_string(self.value)

    def read(self, v):
        self.value = self._param.from_string(v)
        
    def lookup_separated(self, keys):
        if not keys:
            return self
        else:
            raise RuntimeError('Value has no attributes')

    string = property(show, read)

    def set_default(self, default=None):
        self._default = self._param.default if default is None else default

    def get_default(self, default=None):
        try:
            return self._default()
        except TypeError:
            return self._default


    default = property(get_default, set_default)

class NameSpace(object):
    __metaclass__ = ModelMeta
    def __init__(self):
        for name, param in self._params.iteritems():
            setattr(self, name, param)
        self._namespaces = OrderedDict()

    def __setattr__(self, name, obj):
        if isinstance(obj, Param):
            value = Value(obj)
            self._params[name] = obj
            super(NameSpace, self).__setattr__(name, value)
        elif isinstance(obj, NameSpace):
            self._namespaces[name] = obj
            super(NameSpace, self).__setattr__(name, obj)
        else:
            super(NameSpace, self).__setattr__(name, obj)

    def lookup(self, key):
        keys = key.split('.')
        return self.lookup_separated(keys)

    def lookup_separated(self, keys):
        if not keys:
            return self
        return getattr(self, keys[0]).lookup_separated(keys[1:])

Color = String

# This has the potential to be _VERY_ VERY VERY powerful!
class Proxy(Param):
    def __init__(self, dest):
        self._dest = dest

