Introduction
============

Philosophy
----------

Crayon is a a library for drawing that aims to make as few assumptions as possible. Where there are two reasonable ways that the same thing can be communicated, both are allowed and simple rules distinguish which is which. One of the most fundamental design principles is that Crayon should avoid unnecessarily breaking programmer flow. It is also designed to be output-format agnostic.

The core
--------

The most fundamental concept of crayon is the marker. Markers are more than simple coordinates - in crayon, a marker is an immutable reference to a point. You can do what you want with it, but it will always point to the same place on the page. Markers are able to be transformed into multiple coordinate spaces.

Motion
------

Motion is achieved in multiple ways. Each coordinate can be treated as a function.This can be used to provide an absolute coordinate in a space. 

>>> c(10,10)

There are times when you want to move in a direction relative to the current marker. The following 

>>> a = c(0,0).right(10)

Drawing
-------

In order to provide flow, all drawing is performed through markers. Each marker contains a `path'. When a user calls to on a marker, a new marker is constructed with a reference to the previous marker.

>>> c(10,10).to(20,20).draw()

Operators act on the list, and these actions usually change some form of mutable state. For instance, in drawing a path, an encapsulation of global state (the graphics context) will be instructed to change its state.

While most operations are stack based, there are often more conventional counterparts. For instance, c(10,10).rect(20,20) will draw a rectangle that is 20x20 with the bottom-left at the specified point.

Flow
----

Suppose we wish to draw relative to the current available space, for example as with ticks along an axis. We probably want to start in the origin, and then switch into paper coordinate space to move by a fixed rather than relative amount.

>>> for i in ticks:
...     c.plot(0,0).x(i).paper.to.up(5)

When we call paper, we return a view of the current marker in a different coordinate space.

Spaces
------

There are four space that are commonly used.

absolute
  The space on the page relative to the bottom left of the page. This is largely used internally, and is the simplest of all the spaces.

paper
  This is the space you will use the most. It represents the paper on the page, and all dimensions are in millimeters. The origin may not be the bottom left of the page.

box
  This is a space relative to the current box. (0,0) represents the lower left corner of the current box, and (1,1) represents the top right
  
Zooming
-------

Sometimes it is necessary to enlarge a region of the current space. Zooming is achieved by putting the diagonal onto the stack and then calling zoom.

>>> zoomed = c(10,10).to(50,50).zoom

Note that the existing marker remains unmodified. There is no operation that changes markers. For this reason, we have adopted the convention of using brackets only after functions which modify the mutable state. These are usually the last things you wish to do, and may or may not return a modified marker.

This is also very convenient for passing paramters. For instance, the draw, fill, and filldraw actions all take parameters.
