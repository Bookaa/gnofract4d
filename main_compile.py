#!/usr/bin/env python

import sys
from fract4d import fc
from fract4d import fractal, fracttypes
import json

def func4():
    sFile = sys.stdin.readline().strip()
    print 'func4, get length', len(sFile)
    compiler = fc.instance
    compiler.leave_dirty = True
    src = json.loads(sFile)
    #print type(src), len(src)

    node1 = compiler.parse_FormulaFile(str(src))
    sJson = node1.SerialOut()

    print 'next is json'
    print sJson


def docompile():
    stype = sys.stdin.readline().strip()
    if stype == '4':
        return func4()
    print 'stype : <%s>' % stype

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
