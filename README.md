Non-circular Gear Generation Software

Use
===

There are three super-classes (with much duplication), that are subclassed by several self-executable class. Touse them, just invoke the sub-classes from the command line (e.g. '$ python circular-gear.py').

New sub-classes can also be created.


History
=======

Based on work done by Jeff Schoner in his class CS285, Spring 2002 at
UC Berkeley (http://www.cs.berkeley.edu/). http://decidedlyodd.com/cw/cs285/.
His code is published without license, since it is freely available for 8 years
(as of this writing), it is assumed to be in the public domain.

This is also based on work done by Clifford Wolf <clifford@clifford.at>, gearsgen.py, at http://www.thingiverse.com/thing:829, licensed under the GNU, version 2 license.


Disclaimer
=========

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Dependencies
============

* `Python 3.10


License
=======

This is free software, available under the BSD license.


MODULES
=======

There are three types of gears (and accordingly three libraries) that
the system is capable of making. 

slfmaker.py: This is for general gears.  Basically, you give it a
shape, it gives you a dxf file.

conj_slfmaker.py:  This produces a SLIDE file with two conjugate
gears.  One is produced exactly from the description you specify.  The
other is generated as a conjugate to it.

offsetpair_slfmaker.py:  This produces a SLIDE file with two gears
that have an identical shape, but who's teeth are out of phase.  This
module was born out of problems arising with elliptical gears that
would only mesh when the teeth were out of phase with each other.


EXAMPLE
=======

circular_gear.py: This just produces your standard circular gear.  It
was mainly created as a sanity check for the software.  However, it
points out what is necessary:

- You must import the module you want to use.  The circular gear
generator uses the simplest slfmaker.py module.  The file has a first
line of,

from slfmaker import SLFMaker, SLFMakerSphereTeeth

slfmaker contains two classes: SLFMaker which makes actual gears.
SLFMakerSphereTeeth which only makes spheres where the teeth should
be.  This is useful for debugging a description.  Since nothing is
connected, you won't get all that funny twisted back-face garbage if
something is afowl.

The next line imports some useful functions for doing math.  The
system imports these itself for its computations.  But any functions
you need to call in this source file, must be explicitly imported. 

from math import sin,cos,pi,sqrt

- You must extend an existing class:

class circle (SLFMaker):

- A constructor (__init__) is not explicitly necessary for your own
purposes, but the constructor for the parent must be called.  Python
doesn't do this automatically, so it should be the last line in your
constructor. 

- You must specify the following functions that take no explicit
arguments (the first argument in any OO python code is the object on
which the method was called):

  - perimeter (just used as an estimate, so it doesn't by any means
need to be exact) 
  - width (only for SLFMaker's that make more than one gear)

- You must specify the following functions of theta:
  - innerradius (usually just a constant, which will make a circle)
  - outerradius: the actual shape
  - dx: dx/dt
  - dy: dy/dt

- You must do ONE of the following:
  - dx2 (d2x/dt2) and dy2 (d2y/dt2)
  - radiusOfCurvature: used to compute the involute at the tooth at
theta 

If you override radiusOfCurvature, there is no reason to specify dx2
or dy2.  Their only use is by the default method.  dx and dy on the
other hand, must exist even if you do override radiusOfCurvature.
They are also used for teeth orientation.

Note that if these functions are not consistent the following 2 things
may possibly happen:
  - If the first derivative functions are wrong, the teeth will be
oriented strangely and most likely the involute of the teeth will be
messed up.
  - If the second derivative functions are wrong, the involute will be
messed up.
  - In any case where the involute was messed up, the program could
even possibly crash.  Certain mathematical quantities cannot be
negative or beyond [-1,1].

After you have your class designed, you need to create an instance of
it.  Typically, you would pass any shape description values in here
(through the constructor).  You can then call the write method with
the filename you want the output saved to.  The SLFMaker will take
care of the rest.


OTHER EXAMPLES
==============

conj-oval-gear.py: Produces conjugate oval gears with arbitrary period
ratios.

el-gear.py: The standard elliptical gear generator.  Will make offset
pairs for even teeth numbers by default.

oval-gear.py: Makes one oval gear.