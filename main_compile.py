#!/usr/bin/env python

from fract4d import fc
from fract4d import fractal


def docompile():
    compiler = fc.instance
    compiler.leave_dirty = True

    t = fractal.T(compiler)

    outputfile = t.load_and_compile()
    if outputfile:
        print 'success, compile to %s' % outputfile


docompile()