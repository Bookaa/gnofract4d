

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
    the_pf_real.p = params # how to copy ?
    the_pf_real.pos_params = pos_params + []

def calc(** ww):
    the = ww['pfo'] # the is pf_real
    xoff = ww['xoff']
    yoff = ww['yoff']
    xres = ww['xres']
    yres = ww['yres']
    pass

