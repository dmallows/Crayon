# A trial at making auto-scaling boxes.

# Thinking on this, it has become increasingly apparent that dimensions need
# be separated. This doesn't mean that they have to be separated forever, just
# for now. You could always make x-axis and y-axis dependent on each other IF
# THEY NEED TO BE, before passing them. Otherwise, we're being far too specific
# at the expense of flexibility.

# The following is definitely not a waste of time
# So far it has saved an estimated: 1 hour

# ##   #  ####  #### ###    # #####  # #
#  ## #  #  #  #     # ##   #   #    # #
#    #  ####  #   ## #  ##  #   #    # #
#   #  #   #  #    # #   ## #   #   
#  #  #    #   ####  #    ### #####  # #

# The GridLayout is the general case. I think it's probably all we need for
# starting out. That and some mechanism for anchoring boxes to a point. I think
# I have an idea though (think pygame?)

class Box(object):
    def __init__(self, layout=None):
        self.layout = GridLayout() if layout is None else layout
    
    def minimum_size(self):
        pass

class GridLayout(object):
    def __init__(self):
        pass

    def fill(self, iter):
        self.contents = iter
