import importlib
import builtins as __builtin__

try:
    pkg = __name__.rpartition('.')[0]
    mname = '.'.join((pkg, '_lidar2d')).lstrip('.')
    _lidar2d = importlib.import_module(mname)
except ImportError:
    _lidar2d = importlib.import_module('_lidar2d')


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0


class SwigPyIterator(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, SwigPyIterator, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, SwigPyIterator, name)

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr
    __swig_destroy__ = _lidar2d.delete_SwigPyIterator
    __del__ = lambda self: None

    def value(self):
        return _lidar2d.SwigPyIterator_value(self)

    def incr(self, n=1):
        return _lidar2d.SwigPyIterator_incr(self, n)

    def decr(self, n=1):
        return _lidar2d.SwigPyIterator_decr(self, n)

    def distance(self, x):
        return _lidar2d.SwigPyIterator_distance(self, x)

    def equal(self, x):
        return _lidar2d.SwigPyIterator_equal(self, x)

    def copy(self):
        return _lidar2d.SwigPyIterator_copy(self)

    def next(self):
        return _lidar2d.SwigPyIterator_next(self)

    def __next__(self):
        return _lidar2d.SwigPyIterator___next__(self)

    def previous(self):
        return _lidar2d.SwigPyIterator_previous(self)

    def advance(self, n):
        return _lidar2d.SwigPyIterator_advance(self, n)

    def __eq__(self, x):
        return _lidar2d.SwigPyIterator___eq__(self, x)

    def __ne__(self, x):
        return _lidar2d.SwigPyIterator___ne__(self, x)

    def __iadd__(self, n):
        return _lidar2d.SwigPyIterator___iadd__(self, n)

    def __isub__(self, n):
        return _lidar2d.SwigPyIterator___isub__(self, n)

    def __add__(self, n):
        return _lidar2d.SwigPyIterator___add__(self, n)

    def __sub__(self, *args):
        return _lidar2d.SwigPyIterator___sub__(self, *args)
    def __iter__(self):
        return self
SwigPyIterator_swigregister = _lidar2d.SwigPyIterator_swigregister
SwigPyIterator_swigregister(SwigPyIterator)


class VecDouble(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, VecDouble, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, VecDouble, name)
    __repr__ = _swig_repr

    def iterator(self):
        return _lidar2d.VecDouble_iterator(self)
    def __iter__(self):
        return self.iterator()

    def __nonzero__(self):
        return _lidar2d.VecDouble___nonzero__(self)

    def __bool__(self):
        return _lidar2d.VecDouble___bool__(self)

    def __len__(self):
        return _lidar2d.VecDouble___len__(self)

    def __getslice__(self, i, j):
        return _lidar2d.VecDouble___getslice__(self, i, j)

    def __setslice__(self, *args):
        return _lidar2d.VecDouble___setslice__(self, *args)

    def __delslice__(self, i, j):
        return _lidar2d.VecDouble___delslice__(self, i, j)

    def __delitem__(self, *args):
        return _lidar2d.VecDouble___delitem__(self, *args)

    def __getitem__(self, *args):
        return _lidar2d.VecDouble___getitem__(self, *args)

    def __setitem__(self, *args):
        return _lidar2d.VecDouble___setitem__(self, *args)

    def pop(self):
        return _lidar2d.VecDouble_pop(self)

    def append(self, x):
        return _lidar2d.VecDouble_append(self, x)

    def empty(self):
        return _lidar2d.VecDouble_empty(self)

    def size(self):
        return _lidar2d.VecDouble_size(self)

    def swap(self, v):
        return _lidar2d.VecDouble_swap(self, v)

    def begin(self):
        return _lidar2d.VecDouble_begin(self)

    def end(self):
        return _lidar2d.VecDouble_end(self)

    def rbegin(self):
        return _lidar2d.VecDouble_rbegin(self)

    def rend(self):
        return _lidar2d.VecDouble_rend(self)

    def clear(self):
        return _lidar2d.VecDouble_clear(self)

    def get_allocator(self):
        return _lidar2d.VecDouble_get_allocator(self)

    def pop_back(self):
        return _lidar2d.VecDouble_pop_back(self)

    def erase(self, *args):
        return _lidar2d.VecDouble_erase(self, *args)

    def __init__(self, *args):
        this = _lidar2d.new_VecDouble(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def push_back(self, x):
        return _lidar2d.VecDouble_push_back(self, x)

    def front(self):
        return _lidar2d.VecDouble_front(self)

    def back(self):
        return _lidar2d.VecDouble_back(self)

    def assign(self, n, x):
        return _lidar2d.VecDouble_assign(self, n, x)

    def resize(self, *args):
        return _lidar2d.VecDouble_resize(self, *args)

    def insert(self, *args):
        return _lidar2d.VecDouble_insert(self, *args)

    def reserve(self, n):
        return _lidar2d.VecDouble_reserve(self, n)

    def capacity(self):
        return _lidar2d.VecDouble_capacity(self)
    __swig_destroy__ = _lidar2d.delete_VecDouble
    __del__ = lambda self: None
VecDouble_swigregister = _lidar2d.VecDouble_swigregister
VecDouble_swigregister(VecDouble)

class VecVecDouble(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, VecVecDouble, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, VecVecDouble, name)
    __repr__ = _swig_repr

    def iterator(self):
        return _lidar2d.VecVecDouble_iterator(self)
    def __iter__(self):
        return self.iterator()

    def __nonzero__(self):
        return _lidar2d.VecVecDouble___nonzero__(self)

    def __bool__(self):
        return _lidar2d.VecVecDouble___bool__(self)

    def __len__(self):
        return _lidar2d.VecVecDouble___len__(self)

    def __getslice__(self, i, j):
        return _lidar2d.VecVecDouble___getslice__(self, i, j)

    def __setslice__(self, *args):
        return _lidar2d.VecVecDouble___setslice__(self, *args)

    def __delslice__(self, i, j):
        return _lidar2d.VecVecDouble___delslice__(self, i, j)

    def __delitem__(self, *args):
        return _lidar2d.VecVecDouble___delitem__(self, *args)

    def __getitem__(self, *args):
        return _lidar2d.VecVecDouble___getitem__(self, *args)

    def __setitem__(self, *args):
        return _lidar2d.VecVecDouble___setitem__(self, *args)

    def pop(self):
        return _lidar2d.VecVecDouble_pop(self)

    def append(self, x):
        return _lidar2d.VecVecDouble_append(self, x)

    def empty(self):
        return _lidar2d.VecVecDouble_empty(self)

    def size(self):
        return _lidar2d.VecVecDouble_size(self)

    def swap(self, v):
        return _lidar2d.VecVecDouble_swap(self, v)

    def begin(self):
        return _lidar2d.VecVecDouble_begin(self)

    def end(self):
        return _lidar2d.VecVecDouble_end(self)

    def rbegin(self):
        return _lidar2d.VecVecDouble_rbegin(self)

    def rend(self):
        return _lidar2d.VecVecDouble_rend(self)

    def clear(self):
        return _lidar2d.VecVecDouble_clear(self)

    def get_allocator(self):
        return _lidar2d.VecVecDouble_get_allocator(self)

    def pop_back(self):
        return _lidar2d.VecVecDouble_pop_back(self)

    def erase(self, *args):
        return _lidar2d.VecVecDouble_erase(self, *args)

    def __init__(self, *args):
        this = _lidar2d.new_VecVecDouble(*args)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def push_back(self, x):
        return _lidar2d.VecVecDouble_push_back(self, x)

    def front(self):
        return _lidar2d.VecVecDouble_front(self)

    def back(self):
        return _lidar2d.VecVecDouble_back(self)

    def assign(self, n, x):
        return _lidar2d.VecVecDouble_assign(self, n, x)

    def resize(self, *args):
        return _lidar2d.VecVecDouble_resize(self, *args)

    def insert(self, *args):
        return _lidar2d.VecVecDouble_insert(self, *args)

    def reserve(self, n):
        return _lidar2d.VecVecDouble_reserve(self, n)

    def capacity(self):
        return _lidar2d.VecVecDouble_capacity(self)
    __swig_destroy__ = _lidar2d.delete_VecVecDouble
    __del__ = lambda self: None
VecVecDouble_swigregister = _lidar2d.VecVecDouble_swigregister
VecVecDouble_swigregister(VecVecDouble)