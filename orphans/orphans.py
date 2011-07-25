class Coordinates(object):
    def translate(self, dx, dy):
        # Translate by dx, dy.
        return self.transform(lambda x,y: (x+dx, y+dy))

    def transform(self, f):
        return Coordinates(self._transforms + (f,))

    def scale(self, sx, sy):
        # Scale by sx, sy
        return self.transform(lambda x, y: (x*sx, y*sy))
