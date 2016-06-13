#!/usr/bin/env python

import sys
from fract4d import fc
from fract4d import fractal

def docompile():
    
    hash = sys.stdin.readline().strip()
    
    txt = sys.stdin.read()
    # print 'hash:<%s>' % hash
    # print 'txt:<%s>' % txt
    
    compiler = fc.instance
    compiler.leave_dirty = True

    t = fractal.T(compiler)

    outputfile = t.load_and_compile(hash, txt)
    if outputfile:
        print 'success, compile to %s' % outputfile
        


if __name__ == '__main__':
    docompile()
