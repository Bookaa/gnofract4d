#!/usr/bin/env python

import sys, os
from fract4d import fc, fractal #, fracttypes
import json

compiler = fc.instance
compiler.leave_dirty = True

if os.path.isdir('./formulas'):
    compiler.add_func_path("./fract4d")
    compiler.add_func_path("./formulas")
if os.path.isdir('../formulas'):
    compiler.add_func_path("../fract4d")
    compiler.add_func_path("../formulas")

def func4():
    sFile = sys.stdin.readline().strip()
    print 'func4, get length', len(sFile)
    src = json.loads(sFile)
    #print type(src), len(src)

    node1 = compiler.parse_FormulaFile(str(src))
    sJson = node1.SerialOut()

    print 'next is json'
    print sJson

def func1():
    hash = sys.stdin.readline().strip()
    txt = sys.stdin.read()
    print 'func1 hash:<%s>' % hash
    # print 'txt:%s' % txt
    func1_(hash, txt)
    print 'func1_will_return'
    
def func1_(hash, txt):

    t = fractal.T(compiler)

    outputfile = t.load_and_compile(hash, txt)
    if outputfile:
        print 'success, compile to %s' % outputfile


sample_txt = '''gnofract4d formula desc
version=3.10
[function]
formula=[
Mandelbrot {
; The classic Mandelbrot set
init:
	z = #zwpixel
loop:
	z = sqr(z) + #pixel
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
}
]
[endsection]
[outer]
formula=[
continuous_potential {
final:
float ed = @bailout/(|z| + 1.0e-9)
#index = (#numiter + ed) / 256.0
default:
float param bailout
	default = 4.0
endparam
}
]
[endsection]
[inner]
formula=[
zero (BOTH) {
final:
#solid = true
}
]
[endsection]
'''

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        stype = sys.argv[1]
        if stype == '1':
            func1()
        if stype == '4':
            func4()
    else:
        hash = 'ef73a6b2d013623181a159dcc3e3fdaa'
        txt = sample_txt
        func1_(hash, txt)