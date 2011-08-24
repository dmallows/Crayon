"""Validating type system and simple types. It is worth noting that Type objects
only contain information for validation, and a default value. The decision to
use objects to represent types. Inspired by, though no patch on, Haskell's type
system.

Types are class objects, and are transformed using a (simple!) metaclass. When a
NameSpace is instanciated, Value objects are created for each field. These
(confusingly) can contain their own, settable default value, which overrides the
Type's if set. These values contain the current setting, and within a namespace
behave like actual instance objects rather seamlessly.

Children can inherit this behaviour, providing they call the init function.
"""

# Disclaimer: Abandon all hope, ye who enter here.  There is probably far deeper
# magic than we will ever need...  But this is the way the vision came.  So, it
# stays for now!

# TODO: cleanup these exceptions - they're copy & pasted from the python docs!

import re # TODO: remove
from collections import OrderedDict

# =====================
# ===== ERRORS ========
# =====================

class Error(Exception):
    """Generic module Error class, as recommended by Python docs."""
    def __str__(self):
        return '%r: %s' % (self.expr, self.msg)

class ParseError(Error):
    """A string could not be parsed"""
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

class TestError(Error):
    """A test failed to pass"""
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
    def __str__(self):
        return '%s: %s' % (self.expr.__class__.__name__, self.msg)

class Type(object):
    """Base type class"""
    # Counter for ordering (stolen from Django)
    _counter = 0
    def __init__(self, test = None, default = None):
        self._counter = Type._counter
        Type._counter += 1
        self._test = test
        self._default = default
    
    @property
    def default(self):
        """Read only default value for the type."""
        return self._default
    
    def from_py(self, v):
        """Convert from python representation and validate"""
        return self.test(self._from_py(v))

    def _from_py(self, v):
        return v

    def to_py(self, v):
        """Convert from internal representation to python representation"""
        return self._to_py(v)

    def _to_py(self, v):
        return v

    def from_string(self, v):
        """Convert from string and validate"""
        return self.test(self._from_string(v))

    def to_string(self, v):
        """Convert to string"""
        return self._to_string(v)

    def test(self, v):
        """Test the value against the registered tests."""
        f = self._test
        if f:
            f(v)
        return v

#================================
#========== TESTS ===============
#================================
        
# Lambdas have known problems when it comes to pickling. Classes are more solid.
# Here are some classes!  The only requirement of tests is that they are
# callable. So a lambda or a (nested) function is **just** as legitimate.

class RangeTest(object):
    """Check a number is within defined range"""
    def __init__(self, min_ = None, max_ = None):
        self._r = min_, max_

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
    """Check that value is in a given set, naive way"""
    def __init__(self, *ps):
        self._ps = set(ps)
    def __call__(self, v):
        return (v in self._ps)

class ShallowElementTest(object):
    """Check that value is in a given set, using weak equality"""
    def __init__(self, *ps):
        self._ps = ps
    def __call__(self, v):
        for p in self._ps:
            if p is v:
                return True
        return False

class DeepElementTest(object):
    """Check that value is in a given set in a referentially transparent way"""
    def __init__(self, *ps):
        self._ps = ps
    def __call__(self, v):
        for p in self._ps:
            if p == v:
                return True
        return False

class InstanceTest(object):
    """Check that passed item is an instance of a given class"""
    def __init__(self, cls):
        self._cls = cls
    def __call__(self, v):
        return isinstance(v, self._cls)

# TODO: Combinations

#================================
#========== TYPES ===============
#================================

class Boolean(Type):
    def __init__(self, default=False):
        super(Boolean, self).__init__(test=ElementTest(True, False), default=default)

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

class String(Type):
    def __init__(self, default=None):
        super(String, self).__init__(test=InstanceTest(basestring), default=default)

    def _from_string(self, v):
        return v

    def to_string(self, v):
        return v

class Enum(Type):
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

#TODO: represent colors as a proper type!
Color = String

# Numeric types

class Number(Type):
    def __init__(self, min=None, max=None, default=0):
        super(Number, self).__init__(test=RangeTest(min, max), default=default)

class Int(Number):
    def _from_py(self, v):
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

# Polymorphic types (ah yes...)
# It is said that a lot of large scale projects end up re-implementing most
# features of Lisp. It seems that I am re-implementing much of the features of
# Haskell. Python actually makes this *easier* than Haskell (I have a
# disposition towards this kind of thing...). 

class Tuple(Type):
    """Analogue of Python tuples"""
    # TODO: remove regexp. (Serious bugs e.g. parsing strings). Use recursive
    # descent parser instead.
    _r = re.compile(r'\((.*)\)')
    def __init__(self, *params):
        default = tuple(i.default for i in params)
        super(Tuple, self).__init__(default=default)
        self._params = params

    def _from_py(self, values):
        return tuple(p.from_py(v) for p, v in zip(self._params, values))

    def _to_py(self, values):
        return tuple(p.to_py(v) for p, v in zip(self._params, values))

    def _to_string(self, values):
        return '(%s)' % ', '.join(
            p.to_string(v) for p, v in zip(self._params, values))

    def _from_string(self, values):
        return ( p.from_string(v.strip()) for p, v in
                zip(self._params,
                    self._r.match(values).group(1).split(',')) )

class Maybe(Type):
    """Type representing optional parameters"""
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

    def reset(self):
        self._value = None

    value = property(get, set, reset)

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

    def get_default(self):
        try:
            return self._default()
        except TypeError:
            return self._default

    def reset_default(self):
        self._default = self._param.default


    default = property(get_default, set_default, reset_default)

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        params = [(name, attrs.pop(name)) for name, obj in attrs.items() if
                  isinstance(obj, Type)]
        attrs['_params'] = params
        new_class = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        return new_class


class NameSpace(object):
    __metaclass__ = ModelMeta

    def __init__(self):
        super(NameSpace, self).__init__()
        params = self._params
        self._params = OrderedDict()
        self._all = OrderedDict()

        for name, param in params:
            setattr(self, name, param)

        self._namespaces = OrderedDict()

    def __setattr__(self, name, obj):
        if isinstance(obj, Type):
            value = Value(obj)
            self._params[name] = value
            self._all[name] = value
            #super(NameSpace, self).__setattr__(name, Proxy(value))

        elif isinstance(obj, NameSpace):
            self._namespaces[name] = obj
            self._all[name] = obj
            super(NameSpace, self).__setattr__(name, obj)

        elif name in self._params:
            self._params[name].value = obj

        else:
            super(NameSpace, self).__setattr__(name, obj)

    def __getattr__(self, name):
        try:
            return self._params[name].value
        except KeyError:
            return getattr(super(NameSpace, self), name)

    def __delattr__(self, name):
        try:
            del self._params[name].value
        except:
            raise

    def __getitem__(self, name):
        try:
            xs = name.split('.')
            try:
                x, = xs
                try:
                    return self._params[x]
                except:
                    return getattr(self, x)
            except ValueError: # Couldn't unpack => multiple?
                return self[xs]
        except AttributeError: # Couldn't split => list
            try:
                return self[name[0]][name[1:]]
            except TypeError:
                return self[name[0]]

    def __setitem__(self, name, value):
        self._params[name] = value
