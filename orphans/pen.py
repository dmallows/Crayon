class Pen(object):
    def __init__(self, color=(0,0,0), linewidth=0.5):
        # Seriously, 1mm? Biro looks about 0.5mm. Changing.
        self.color = color
        self.linewidth = linewidth

    def set_rgb(self, r,g,b):
        """Set the current colour"""
        self.color = (r, g, b)

    def set_linewidth(self, linewidth):
        """Set the current linewidth"""
        self.linewidth = linewidth
