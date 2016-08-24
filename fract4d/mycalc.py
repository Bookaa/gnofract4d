import numba
from numba import jit, types, int64, float64, complex128, typeof # 0.27.0

(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)


@jit(float64(complex128), nopython=True, nogil=True)
def abs2(c):
    return c.imag * c.imag + c.real * c.real

@jit(types.Tuple((int64,int64,complex128))(float64, complex128, complex128, int64), nopython=True, nogil=True)
def Mandelbrot_1(fbailout, pixel, zwpixel, maxiter):
    '''
    Mandelbrot {
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
    '''

    #print str(type(fbailout)), str(type(pixel)), str(type(zwpixel)), str(type(maxiter))
    t__h_numiter = 0
    z = zwpixel
    t__h_inside = 0
    while True:
        z = z*z + pixel
        if abs2(z) >= fbailout:
            break
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break
    return t__h_inside, t__h_numiter, z

@jit(types.Tuple((int64,int64,complex128))(complex128, complex128, int64), nopython=True, nogil=True)
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
        z = z - p1 * (z3 - pixel) / (z2 * 3.0)
        if abs2(z3 - pixel) <= 0.0001:
            break
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break

    return t__h_inside, t__h_numiter, z


@jit(types.Tuple((int64,int64,complex128))(complex128, float64, complex128, complex128, int64), nopython=True, nogil=True)
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
    return t__h_inside, t__h_numiter, z
