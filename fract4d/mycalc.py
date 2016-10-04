import numba
from numba import jit, types, int64, float64, complex128, typeof # 0.27.0

(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)

DISABLE_JIT = False
if DISABLE_JIT:
    numba.config.DISABLE_JIT = True

def myjit(*args, **kws):
    kws.update({'nopython': True})
    kws.update({'nogil': True})
    # kws.update({'cache': True})
    return jit(*args, **kws)

def myjitclass(spec):
    return numba.jitclass(spec)

@myjit(float64(complex128))
def abs2(c):
    return c.imag * c.imag + c.real * c.real

@numba.cfunc('float64(complex128)')
def abs3(c):
    return c.imag * c.imag + c.real * c.real

@numba.cfunc('float64(float64,float64)')
def abs4(i,r):
    return i*i+r*r

#pro_abs4 = CFUNCTYPE(c_double,c_double,c_double)(abs4)
pro_abs4 = abs4.ctypes

if __name__ == '__main__':

    #print Mandelbrot_1.inspect_llvm().values()[0]
    #print CGNewton3_1.inspect_llvm().values()[0]
    print Cubic_Mandelbrot_1.inspect_llvm().values()[0]
    #print abs2.inspect_llvm().values()[0]

    #t__a_fbailout, pixel, zwpixel, maxiter = 4.0, (-0.805474821772-0.180754042393j), 0j, 2008

    #print Mandelbrot_1(t__a_fbailout, pixel, zwpixel, maxiter)

    #import pdb; pdb.set_trace()