class LinkedList(object):
    def __init__(self, x = None, xs = None)
        self.x  = x
        self.xs = xs

    def cons(self, payload):
        return LinkedList(payload, self)

    def pop(self):
        return self.payload, self.xs

    def __repr__(self):
        return '[%s]' % ', '.join(repr(i) for i in self)

    def __iter__(self):
        return LinkedListIterator(self)

class LinkedListIterator(object):
    def __init__(self, xs):
        self.xs = xs

    def next(self):
        try:
            x, xs = self.xs.pop()
            self.xs = xs
            return x
        except AttributeError, e:
            raise StopIteration()
