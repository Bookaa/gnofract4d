
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

def init(the_pf_real, pos_params, params):
    the_pf_real.pfo.p = params # how to copy ?
    the_pf_real.pfo.pos_params = pos_params + []

def calc(pfo, params, maxiter):
    fUseColors = 0
    colors = [0.0, 0.0, 0.0, 0.0]
    solid = 0;
    dist = 0.0;
    iter_ = 0;
    fate = 0

    pixel = complex(params[0], params[1])
    t__h_zwpixel = complex(params[2], params[3])

    # print dir(pfo.p[5])
    t__a_cf1_offset = pfo.p[5].doubleval
    t__a_fbailout = pfo.p[1].doubleval
    t__a_cf0_density = pfo.p[3].doubleval
    t__a_cf0_offset = pfo.p[2].doubleval
    t__a_cf0bailout = pfo.p[4].doubleval

    save_mask = 9
    save_incr = 1
    t__h_numiter = 0
    z = t__h_zwpixel
    old_z = z
    while True:
        z = z*z + pixel
        if abs(z)*abs(z) >= t__a_fbailout:
            t__h_inside = (t__h_numiter >= maxiter)
            break
        if t__h_numiter >= maxiter:
            if t__h_numiter & sav_mask:
                if abs(z.real - old_z.real) < period_tolerance and abs(z.imag - old_z.imag) < period_tolerance:
                    t__h_inside = 1
                    break
            else:
                old_z = z
                save_incr -= 1
                if save_incr == 0:
                    save_mask = (save_mask << 1) + 1
                    save_incr = next_save_incr
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break
    iter_ = t__h_numiter
    if t__h_inside == 0:
        solid = 0
        t__cf03 = abs(z) * abs(z) + 0.000000001
        t__cf04 = t__a_cf0bailout / t__cf03
        t__cf06 = t__h_numiter + t__cf04
        t__cf08 = t__a_cf0_density * t__cf06 / 256.0
        t__h_index = t__cf08 + t__a_cf0_offset
    else:
        solid = 1
        t__h_index = t__a_cf1_offset
    fate = FATE_INSIDE if t__h_inside != 0 else 0
    dist = t__h_index
    if solid:
        fate |= FATE_SOLID
    if fUseColors:
        fate |= FATE_DIRECT
    if fate & FATE_INSIDE:
        iter_ = -1
    return fUseColors, colors, solid, dist, iter_, fate
