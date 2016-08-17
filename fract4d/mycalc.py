
(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)

'''
typedef enum
{
    INT = 0,
    FLOAT = 1,
    GRADIENT = 2,
    PARAM_IMAGE = 3
} e_paramtype;

struct s_param
{
    e_paramtype t;
    int intval;
    double doubleval;
    void *gradient;
    void *image;
};
'''

PF_MAXPARAMS = 200
N_PARAMS = 11

class s_param:
    pass

def parse_params(params):
    lst = []
    import gradient
    for itm in params:
        the = s_param()
        if isinstance(itm, gradient.Gradient):
            the.t = 2 # GRADIENT
            the.gradient = itm
        elif isinstance(itm, float):
            the.t = 1 # FLOAT
            the.doubleval = itm
        else:
            assert False
        lst.append(the)
    return lst

class pf_real:
    def __init__(self):
        # self.p = [None] * PF_MAXPARAMS
        p = []
        for i in range(PF_MAXPARAMS):
            the = s_param()
            p.append(the)
        self.p = p
        self.pos_params = [0.0] * N_PARAMS

def pf_new():
    the = pf_real()
    return the

def Mandelbrot_calc(pfo_p, params, maxiter):
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
    fUseColors = 0
    colors = [0.0, 0.0, 0.0, 0.0]

    pixel = complex(params[0], params[1])
    t__h_zwpixel = complex(params[2], params[3])

    t__a_cf1_offset = pfo_p[5].doubleval
    t__a_fbailout = pfo_p[1].doubleval
    t__a_cf0_density = pfo_p[3].doubleval
    t__a_cf0_offset = pfo_p[2].doubleval
    t__a_cf0bailout = pfo_p[4].doubleval

    t__h_numiter = 0
    z = t__h_zwpixel
    t__h_inside = 0
    while True:
        z = z*z + pixel
        if abs2(z) >= t__a_fbailout:
            break
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break
    iter_ = t__h_numiter
    if t__h_inside == 0:
        t__cf03 = abs2(z) + 0.000000001
        t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        t__h_index = t__a_cf0_density * t__cf06 / 256.0 + t__a_cf0_offset
    else:
        t__h_index = t__a_cf1_offset
    fate = FATE_INSIDE if t__h_inside != 0 else 0
    dist = t__h_index
    solid = t__h_inside
    if solid:
        fate |= FATE_SOLID
    if fUseColors:
        fate |= FATE_DIRECT
    if fate & FATE_INSIDE:
        iter_ = -1
    return fUseColors, colors, solid, dist, iter_, fate

def CGNewton3_calc(pfo_p, params, maxiter):
    '''
    CGNewton3 {
      z=(1,1):
       z2=z*z
       z3=z*z2
       z=z-p1*(z3-pixel)/(3.0*z2)
        0.0001 < |z3-pixel|
      }
    '''
    fUseColors = 0
    colors = [0.0, 0.0, 0.0, 0.0]

    pixel = complex(params[0], params[1])
    # t__h_zwpixel = complex(params[2], params[3])

    t__a_cf1_offset = pfo_p[5+1].doubleval
    # t__a_fbailout = pfo_p[1].doubleval
    t__a_cf0_density = pfo_p[3+1].doubleval
    t__a_cf0_offset = pfo_p[2+1].doubleval
    t__a_cf0bailout = pfo_p[4+1].doubleval

    t__h_numiter = 0
    z = complex(1.0, 1.0)

    p1 = complex(pfo_p[1].doubleval, pfo_p[2].doubleval)

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
    iter_ = t__h_numiter
    if t__h_inside == 0:
        t__cf03 = abs2(z) + 0.000000001
        t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        t__h_index = t__a_cf0_density * t__cf06 / 256.0 + t__a_cf0_offset
    else:
        t__h_index = t__a_cf1_offset

    fate = FATE_INSIDE if t__h_inside != 0 else 0
    dist = t__h_index
    solid = t__h_inside
    if solid:
        fate |= FATE_SOLID
    if fUseColors:
        fate |= FATE_DIRECT
    if fate & FATE_INSIDE:
        iter_ = -1
    return fUseColors, colors, solid, dist, iter_, fate

def abs2(c):
    return c.imag * c.imag + c.real * c.real