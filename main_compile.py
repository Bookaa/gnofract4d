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
    # print 'func4, get length', len(sFile)
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
    print 'txt:%s' % txt
    return func1_(hash, txt)
    
def func1_(hash, txt):

    t = fractal.T(compiler)

    outputfile = t.load_and_compile(hash, txt)
    if outputfile:
        print 'success, compile to %s' % outputfile



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
        txt = 'gnofract4d formula desc\nversion=3.10\n[function]\nformulafile=gf4d.frm\nfunction=Mandelbrot\nformula=[\nMandelbrot {\n; The classic Mandelbrot set\ninit:\n\tz = #zwpixel\nloop:\n\tz = sqr(z) + #pixel\nbailout:\n\t@bailfunc(z) < @bailout\ndefault:\nfloat param bailout\n\tdefault = 4.0\nendparam\nfloat func bailfunc\n\tdefault = cmag\nendfunc\n}\n]\n[endsection]\n[outer]\nformulafile=gf4d.cfrm\nfunction=continuous_potential\nformula=[\ncontinuous_potential {\nfinal:\nfloat ed = @bailout/(|z| + 1.0e-9) \n#index = (#numiter + ed) / 256.0\ndefault:\nfloat param bailout\n\tdefault = 4.0\nendparam\n}\n]\n[endsection]\n[inner]\nformulafile=gf4d.cfrm\nfunction=zero\nformula=[\nzero (BOTH) {\nfinal:\n#solid = true\n}\n]\n[endsection]\n[transform]=0\nformulafile=gf4d.uxf\nfunction=Inverse\nformula=[\nInverse {\n;\n; Inverts the complex plane before calculating the fractal.\n; Essentially turns the fractal "inside out".\n;\ntransform:\n  #pixel = @center + @radius / (#pixel - @center)\ndefault:\n  title = "Inverse"\n  float param radius\n    caption = "Radius"\n    default = 1.0\n    hint = "This is the radius of the inversion circle. Larger values \\\n            magnify the fractal."\n    min = 0\n  endparam\n  complex param center\n    caption = "Center"\n    default = (0, 0)\n    hint = "This is the center of the inversion circle."\n  endparam\n}\n]\n[endsection]\n\n\n'
        func1_(hash, txt)