import numba
from numba import jit, types, int64, float64, complex128, typeof # 0.27.0

(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)

UseLLVM = True

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

import math

@myjit(types.Tuple((int64,int64,complex128,float64,int64))(float64, complex128, complex128, int64))
def Mandelbrot_1(fbailout, pixel, zwpixel, maxiter):
    '''
    Mandelbrot with inside = Angles
    '''
    min_period_iter=10
    period_tolerance=0.0001
    save_mask = 9
    save_incr = 1
    next_save_incr = 4

    t__h_numiter = 0
    z = zwpixel
    t__h_inside = 0

    old_z = z

    if False:
        angle = math.pi
    while True:
        z = z*z + pixel
        if z.real * z.real + z.imag * z.imag >= fbailout:
            break

        if t__h_numiter >= min_period_iter:
            if (t__h_numiter & save_mask) == 0:
                old_z = z
                save_incr -= 1
                if save_incr == 0:
                    save_mask = (save_mask << 1) + 1
                    save_incr = next_save_incr
            else:
                if math.fabs(z.real - old_z.real) < period_tolerance and math.fabs(z.imag - old_z.imag) < period_tolerance:
                    t__h_inside = 1
                    break

        if False:
            temp_angle = math.fabs(math.atan2(z.imag, z.real))
            if temp_angle < angle:
                angle = temp_angle

        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break

    solid = 0
    if t__h_inside == 0:
        t__a_cf0bailout = 4.0
        t__cf03 = abs2(z) + 0.000000001
        t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        idex = t__cf06 / 256.0 # t__a_cf0_density * t__cf06 / 256.0 + t__a_cf0_offset
        '''
        continuous_potential {
final:
float ed = @bailout/(|z| + 1.0e-9)
#index = (#numiter + ed) / 256.0
default:
float param bailout
	default = 4.0
endparam
}
        '''
    else:
        if True: # for basins
            nbasins = 3
            if False:
                #idex = (t__h_numiter / 256.0) % nbasins
                idex = (t__h_numiter * 1.0 / 256.0) + nbasins
                #idex = math.fmod(t__h_numiter / 256.0, nbasins)
            else:
                idex = 0 # fate * 1.0/@nbasins)
                idex = idex + (t__h_numiter / 256.0) % nbasins
                #idex = math.fmod(t__h_numiter / 256.0, nbasins)

            #print idex, t__h_numiter,
        elif True: # for zero
            idex = 0 #t__a_cf1_offset
            solid = 1
        else: # for angel
            idex = angle / math.pi

    return t__h_inside, t__h_numiter, z, idex, solid

@myjit(types.Tuple((int64,int64,complex128,float64,int64))(complex128, complex128, int64))
def CGNewton3_1(p1, pixel, maxiter):
    '''
    CGNewton3 {
      z=(1,1):
       z2=z*z
       z3=z*z2
       z=z-p1*(z3-pixel)/(3.0*z2)
        0.0001 < |z3-pixel|
      }
    '''

    t__h_numiter = 0
    z = complex(1.0, 1.0)

    t__h_inside = 0
    while True:
        z2 = z * z
        z3 = z * z2
        z4 = z3 - pixel
        z = z - p1 * z4 / (z2 * 3.0)
        if z4.real * z4.real + z4.imag * z4.imag <= 0.0001:
            break
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break

    solid = 0
    if t__h_inside == 0:
        t__a_cf0bailout = 4.06664633010422705
        t__cf03 = abs2(z) + 0.000000001
        t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        idex = t__cf06 / 256.0 # t__a_cf0_density * t__cf06 / 256.0 + t__a_cf0_offset
    else:
        idex = 0 #t__a_cf1_offset
        solid = 1

    return t__h_inside, t__h_numiter, z, idex, solid


@myjit(types.Tuple((int64,int64,complex128,float64,int64))(complex128, float64, complex128, complex128, int64))
def Cubic_Mandelbrot_1(fa, fbailout, pixel, zwpixel, maxiter):
    '''
    Cubic Mandelbrot {
    ; z <- z^3 + c
    ; The cubic set actually has two critical values, but this formula just uses
    ; zero - to be fixed later.
    init:
        z = #zwpixel
        ; nothing to do here
    loop:
        z = z * z * (z - 3.0 * @a) + #pixel
    bailout:
        @bailfunc(z) < @bailout
    default:
    float param bailout
        default = 4.0
    endparam
    float func bailfunc
        default = cmag
    endfunc
    complex param a
        default = (0.0,0.0)
    endparam
    }
    '''
    t__h_numiter = 0
    z = zwpixel
    t__h_inside = 0
    while True:
        z = z*z*(z - fa * 3.0) + pixel
        if abs2(z) >= fbailout:
            break
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break

    solid = 0
    if t__h_inside == 0:
        t__a_cf0bailout = 4.0
        t__cf03 = abs2(z) + 0.000000001
        t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        idex = t__cf06 / 256.0 # t__a_cf0_density * t__cf06 / 256.0 + t__a_cf0_offset
    else:
        idex = 0 #t__a_cf1_offset
        solid = 1

    return t__h_inside, t__h_numiter, z, idex, solid

if __name__ == '__main__':

    #print Mandelbrot_1.inspect_llvm().values()[0]
    #print CGNewton3_1.inspect_llvm().values()[0]
    print Cubic_Mandelbrot_1.inspect_llvm().values()[0]
    #print abs2.inspect_llvm().values()[0]

    #t__a_fbailout, pixel, zwpixel, maxiter = 4.0, (-0.805474821772-0.180754042393j), 0j, 2008

    #print Mandelbrot_1(t__a_fbailout, pixel, zwpixel, maxiter)

    #import pdb; pdb.set_trace()