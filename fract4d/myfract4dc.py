import math
import numpy as np
import numba
from numba import jit, types, typeof, none, boolean, byte, int64, float64, complex128 # 0.27.0
import mycalc

from mycalc import myjit, myjitclass

(VX, VY, VZ, VW) = (0,1,2,3)
(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_TOTAL_WIDTH, IMAGE_TOTAL_HEIGHT, IMAGE_XOFFSET, IMAGE_YOFFSET) = (0,1,2,3,4,5)
(XCENTER, YCENTER, ZCENTER, WCENTER, MAGNITUDE, XYANGLE, XZANGLE, XWANGLE, YZANGLE, YWANGLE, ZWANGLE) = (0,1,2,3,4,5,6,7,8,9,10)
(RED, GREEN, BLUE) = (0, 1, 2)
(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)
(RGB, HSV_CCW, HSV_CW) = (0, 1, 2)
(BLEND_LINEAR,BLEND_CURVED,BLEND_SINE,BLEND_SPHERE_INCREASING,BLEND_SPHERE_DECREASING) = (0,1,2,3,4)
N_SUBPIXELS = 4
N_PARAMS = 11

Image_spec = [
    ('m_Xres', int64),
    ('m_Yres', int64),
    ('m_totalXres', int64),
    ('m_totalYres', int64),
    ('m_xoffset', int64),
    ('m_yoffset', int64),
    ('buffer', numba.u1[:]),
    ('iter_buf', int64[:]),
    ('fate_buf', numba.u1[:]),
    ('index_buf', float64[:]),
    ('lastIter', int64),
]

@myjitclass(Image_spec)
class Image(object):
    def __init__(self):
        self.m_Xres = self.m_Yres = 0
        self.m_totalXres = self.m_totalYres = 0
        self.m_xoffset = self.m_yoffset = 0
        self.buffer = np.zeros(0,dtype=np.uint8) #None
        self.iter_buf = np.zeros(0,dtype=np.int64) #None
        self.fate_buf = np.zeros(0,dtype=np.uint8) #None
        self.index_buf = np.zeros(0,dtype=np.float64) #None
        self.lastIter = 0

    def Xres(self): return self.m_Xres
    def Yres(self): return self.m_Yres
    def totalXres(self): return self.m_totalXres
    def totalYres(self): return self.m_totalYres
    def Xoffset(self): return self.m_xoffset
    def Yoffset(self): return self.m_yoffset
    def row_length(self): return self.Xres() * 3
    def bytes(self): return self.row_length() * self.m_Yres

    def periodGuess(self, periodicity, maxiter):
        if not periodicity:
            return maxiter
        if self.lastIter == -1:
            return 0
        return self.lastIter + 10

        '''
        if(!ff->periodicity)
            return ff->maxiter;
        if(lastIter == -1)
        {
        // we were captured last time so probably will be again
        return 0;
        }
        // we escaped, so don't try so hard this time
        return lastIter + 10;
        '''
    def periodSet(self, iter_):
        self.lastIter = iter_

    def alloc_buffers(self):
        self.buffer = np.zeros(self.bytes(),dtype=np.uint8)
        self.iter_buf = np.zeros(self.m_Xres * self.m_Yres,dtype=np.int64)

        MAX_RECOLOR_SIZE  = 1024*768

        if self.m_Xres * self.m_Yres <= MAX_RECOLOR_SIZE:
            self.index_buf = np.zeros(self.m_Xres * self.m_Yres * N_SUBPIXELS,dtype=np.float64)
            self.fate_buf = np.zeros(self.m_Xres * self.m_Yres * N_SUBPIXELS,dtype=np.uint8)
        else:
            self.index_buf = np.zeros(0,dtype=np.float64)
            self.fate_buf = np.zeros(0,dtype=np.uint8)
        self.clear()

    def clear(self):
        fate_pos = 0
        for y in range(self.m_Yres):
            for x in range(self.m_Xres):
                self.iter_buf[y*self.m_Xres + x] = -1
                for n in range(N_SUBPIXELS):
                    self.fate_buf[fate_pos] = FATE_UNKNOWN
                    fate_pos += 1

    def set_resolution(self, x, y, totalx, totaly):
        totalx = x if (totalx == -1) else totalx
        totaly = y if (totaly == -1) else totaly

        if len(self.buffer) and \
           self.m_Xres == x and self.m_Yres == y and \
           self.m_totalXres == totalx and self.m_totalYres == totaly:
           return

        self.m_Xres = x
        self.m_Yres = y
        self.m_totalXres = totalx
        self.m_totalYres = totaly

        self.alloc_buffers()

        pixel = np.array([0,0,0,255], dtype = np.uint8)

        for i in range(y):
            for j in range(x):
                self.put(j,i,pixel)

    def set_offset(self, x, y):
        self.m_xoffset = x
        self.m_yoffset = y

    def put(self, x, y, pixel):
        r,g,b,a = pixel
        off = x * 3 + y * self.m_Xres * 3
        self.buffer[off+0] = r # red
        self.buffer[off+1] = g # green
        self.buffer[off+2] = b # blue

    def getFate(self, x, y, subpixel):
        n = self.index_of_subpixel(x,y,subpixel)
        return self.fate_buf[n]
    def index_of_subpixel(self,x,y,subpixel):
        return (y * self.m_Xres + x) * N_SUBPIXELS + subpixel
    def setIter(self,x,y,iter):
        self.iter_buf[x + y * self.m_Xres] = iter
    def setFate(self,x,y,subpixel,fate):
        i = self.index_of_subpixel(x,y,subpixel)
        self.fate_buf[i] = fate
    def setIndex(self,x,y,subpixel,index):
        i = self.index_of_subpixel(x,y,subpixel)
        self.index_buf[i] = index
    def getIter(self, x, y):
        return self.iter_buf[x + y * self.m_Xres]
    def get(self, x, y):
        pos = x * 3 + y * self.m_Xres * 3
        r = self.buffer[pos + RED]
        g = self.buffer[pos + GREEN]
        b = self.buffer[pos + BLUE]
        return np.array([r,g,b,0], dtype = np.uint8)
    def getIndex(self,x,y,subpixel):
        n = self.index_of_subpixel(x,y,subpixel)
        return self.index_buf[n]

tem33 = Image()

typeof_Image = typeof(tem33)

del tem33

ii_spec = [
    ('im', typeof_Image),
    ('index', float64),
    ('iter', int64),
    ('fate', numba.uint8),
    ('pixel', numba.uint8[:]),
]

@myjitclass(ii_spec)
class im_info(object):
    def __init__(self, im):
        self.im = im
        self.index = 0.0
        self.iter = 0
        self.fate = 0
        self.pixel = np.array([0,0,0,0], dtype=np.uint8)
    def init_fate(self, x, y):
        self.index = 0.0
        self.iter = 0
        self.fate = self.im.getFate(x,y,0)
    def init(self, x, y):
        self.index = self.im.getIndex(x,y,0)
        self.iter = self.im.getIter(x,y)
        self.fate = self.im.getFate(x,y,0)
        self.pixel = self.im.get(x,y)
        pass
    def writeback(self, x, y):
        self.im.setIter(x,y,self.iter)
        self.im.setFate(x,y,0,self.fate)
        self.im.setIndex(x,y,0,self.index)
    def rectangle(self,x,y,w,h):
        for i in range(y, y+h):
            for j in range(x, x+w):
                self.im.put(j,i,self.pixel)
    def rectangle_with_iter(self,x,y,w,h):
        for i in range(y, y+h):
            for j in range(x, x+w):
                self.im.put(j,i,self.pixel)
                self.im.setIter(j,i,self.iter)
                self.im.setFate(j,i,0,self.fate)
                self.im.setIndex(j,i,0,self.index)
    def set_pixel(self, pixel):
        self.pixel = pixel
tem32 = Image()
tem33 = im_info(tem32)
typ_im_info = typeof(tem33)
del tem33
del tem32

def cmap_from_pyobject(segs):
    n = len(segs)
    cmap_items = [] # ColorMap(n)
    for i in range(n):
        # the = gradient_item_t()
        left = segs[i].left
        right = segs[i].right
        mid = segs[i].mid
        cmode = segs[i].cmode
        bmode = segs[i].bmode
        left_col = segs[i].left_color
        right_col = segs[i].right_color

        (f1,f2,f3,f4) = left_col
        leftc = (f1,f2,f3,f4)
        (f1,f2,f3,f4) = right_col
        rightc = (f1,f2,f3,f4)
        #n = len(left_col)
        #leftc = np.zeros(n,dtype=np.float64)
        #for j in range(n):
        #    leftc[j] = left_col[j]

        #n = len(right_col)
        #rightc = np.zeros(n,dtype=np.float64)
        #for j in range(n):
        #    rightc[j] = right_col[j]

        the = (left, right, mid, bmode, cmode, leftc, rightc)
        ''' gradient_item_t_spec = [
            ('left', float64),
            ('right', float64),
            ('bmode', int64),
            ('cmode', int64),
            ('mid', float64),
            ('left_color', float64[:]),
            ('right_color', float64[:]),
        ]'''

        # the.set(left, right, mid, left_col, right_col, bmode, cmode)
        cmap_items.append(the)
    n = len(cmap_items)
    cmap_arr = np.zeros(n, dtype=dtype_cmap)
    for i in range(n):
        (f0,f1,f2,i1,i2,(f3,f4,f5,f6),(f7,f8,f9,f10)) = cmap_items[i]
        cmap_arr[i]['f0'] = f0
        cmap_arr[i]['f1'] = f1
        cmap_arr[i]['f2'] = f2
        cmap_arr[i]['i1'] = i1
        cmap_arr[i]['i2'] = i2
        cmap_arr[i]['f3'] = f3
        cmap_arr[i]['f4'] = f4
        cmap_arr[i]['f5'] = f5
        cmap_arr[i]['f6'] = f6
        cmap_arr[i]['f7'] = f7
        cmap_arr[i]['f8'] = f8
        cmap_arr[i]['f9'] = f9
        cmap_arr[i]['f10'] = f10

    return cmap_arr

def calc_7(pfcls, xoff, yoff, xres, yres):
    (self_params, self_cmap, im, self_maxiter, periodicity, period_tolerance) = pfcls

    xtotalsize = im.totalXres()
    ytotalsize = im.totalYres()
    im.set_resolution(xres, yres, xtotalsize, ytotalsize)
    im.set_offset(xoff, yoff)

    (ff_deltax, ff_deltay, ff_topleft) = GetPos_delta(im, self_params)

    ff = (ff_topleft, ff_deltax, ff_deltay, self_maxiter, periodicity, period_tolerance)

    stfw = (self_cmap, im, ff)

    draw_8(stfw)

def image_create(xsize, ysize, txsize, tysize):
    img = Image()
    img.set_resolution(xsize, ysize, txsize, tysize)
    return img
    #_img = fract4dc.image_create(xsize, ysize, txsize, tysize)

def image_dims(_img):
    xsize = _img.Xres()
    ysize = _img.Yres()
    xoffset = _img.Xoffset()
    yoffset = _img.Yoffset()
    xtotalsize = _img.totalXres()
    ytotalsize = _img.totalYres()
    return (xsize, ysize, xtotalsize, ytotalsize, xoffset, yoffset)

typ34 = types.Tuple((float64,float64,float64,float64,float64))
typ_pfo_p = types.Tuple((typ34, typ34))

typ36 = types.Tuple((float64, float64, float64, int64, int64,
                     types.Tuple((float64, float64, float64, float64)),
                     types.Tuple((float64, float64, float64, float64))
                     ))

typ_cmap = types.List(typ36, reflected=True)

tem33 = np.array([0.0,0.0,0.0,0.0], dtype = np.float64)
typeof_dbl4 = typeof(tem33)
del tem33
typ_ff = types.Tuple((typeof_dbl4, typeof_dbl4, typeof_dbl4, int64))
typ_stfw = types.Tuple((typ_pfo_p, typ_cmap, typeof_Image, int64, typ_ff))

tem33 = np.array([0,0,0,0], dtype = np.uint8)
typeof_array4 = typeof(tem33)
del tem33

@myjit(int64(typeof_array4))
def Pixel2INT(pixel):
    r,g,b,a = pixel
    return (r << 16) | (g << 8) | b

@myjit(int64(typeof_Image, int64, int64))
def RGB2INT(im,x,y):
    pixel = im.get(x,y)
    return Pixel2INT(pixel)

@myjit(boolean(typeof_Image, boolean, int64, int64, int64, int64))
def isTheSame(im, bFlat, targetIter, targetCol, x, y):
    if not bFlat:
        return False
    if im.getIter(x,y) != targetIter:
        return False
    if RGB2INT(im,x,y) != targetCol:
        return False
    return True

@myjit(float64(float64,float64))
def calc_linear_factor(middle, pos):
    EPSILON = 1e-10
    if pos <= middle:
        if middle < EPSILON:
            return 0.0
        return 0.5 * pos / middle
    else:
        pos -= middle
        middle = 1.0 - middle
        if middle < EPSILON:
            return 1.0
        return 0.5 + 0.5 * pos / middle

@myjit(float64(float64,float64))
def calc_sphere_decreasing_factor(middle, pos):
    pos = calc_linear_factor(middle, pos)
    return 1.0 - math.sqrt(1.0 - pos * pos)

@myjit(float64(float64,float64))
def calc_sphere_increasing_factor(middle, pos):
    pos = calc_linear_factor(middle, pos) - 1.0
    return math.sqrt(1.0 - pos * pos)

@myjit(float64(float64,float64))
def calc_sine_factor(middle, pos):
    pos = calc_linear_factor(middle, pos)
    return (math.sin((-math.pi / 2.0) + math.pi * pos) + 1.0) / 2.0

@myjit(float64(float64,float64))
def calc_curved_factor(middle, pos):
    EPSILON = 1e-10
    middle = max(middle, EPSILON)
    return math.pow(pos, math.log(0.5)) / math.log(middle)

@myjit(types.Tuple((float64,float64,float64))(float64,float64,float64))
def hsv_to_rgb(h,s,v):
    if s == 0:
        return (v,v,v)
    while h > 6.0:
        h -= 6.0
    if h < 0:
        h += 6.0
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    elif i == 5:
        return (v, p, q)
    else:
        #assert False
        return (0.0, 0.0, 0.0)
@myjit(types.Tuple((float64,float64,float64))(float64,float64,float64))
def gimp_hsv_to_rgb(h,s,v):
    return hsv_to_rgb(h * 6.0, s, v)

dtype_cmap = np.dtype([('f0','f8'),('f1','f8'),('f2','f8'),
                       ('i1','i8'),('i2','i8'),
                       ('f3','f8'),('f4','f8'),('f5','f8'),('f6','f8'),
                       ('f7','f8'),('f8','f8'),('f9','f8'),('f10','f8')])

typ_np_cmap = typeof(np.zeros(1, dtype=dtype_cmap))

@myjit(int64(float64,typ_np_cmap,int64))
def grad_find(index, items, ncolors):

    i = ncolors - ncolors

    while i < ncolors:
        #(left, right, mid, bmode, cmode, leftc, rightc) = items[i]
        right = items[i]['f1']
        if index <= right:
            return i
        i+=1

    return -1

@myjit(types.Tuple((float64,float64,float64))(float64,float64,float64))
def rgb_to_hsv(r,g,b):
    min_ = min(r,g,b)
    max_ = max(r,g,b)
    v = max_
    delta = max_ - min_
    s = 0.0 if max_ == 0.0 else delta / max_
    if s == 0.0:
        h = 0.0
        return (h,s,v)
    if r == max_:
        h = (g - b) / delta
    elif g == max_:
        h = 2.0 + (b - r) / delta
    else:
        h = 4.0 + (r - g) / delta
    if h < 0.0:
        h += 6.0
    return (h, s, v)
@myjit(types.Tuple((float64,float64,float64))(float64,float64,float64))
def gimp_rgb_to_hsv(r,g,b):
    (h,s,v) = rgb_to_hsv(r,g,b)
    return (h / 6.0, s, v)

@myjit(types.Tuple((byte, byte, byte, byte))(typ_np_cmap, float64))
def look33up(cmap_items, input_index):
    self_items = cmap_items
    self_ncolors = len(cmap_items)
    index = 1.0 if input_index == 1.0 else input_index - int(input_index)
    i = grad_find(index, self_items, self_ncolors)
    seg = self_items[i]
    #(seg_left, seg_right, seg_mid, seg_bmode, seg_cmode, seg_left_color, seg_right_color) = seg
    seg_left = seg['f0']
    seg_right = seg['f1']
    seg_mid = seg['f2']
    seg_bmode = seg['i1']
    seg_cmode = seg['i2']
    seg_left_color = (seg['f3'],seg['f4'],seg['f5'],seg['f6'])
    seg_right_color = (seg['f7'],seg['f8'],seg['f9'],seg['f10'])

    seg_len = seg_right - seg_left
    EPSILON = 1e-10
    if seg_len < EPSILON:
        middle = 0.5
        pos = 0.5
    else:
        middle = (seg_mid - seg_left) / seg_len
        pos = (index - seg_left) / seg_len
    if seg_bmode == BLEND_LINEAR:
        factor = calc_linear_factor(middle, pos)
    elif seg_bmode == BLEND_CURVED:
        factor = calc_curved_factor(middle, pos)
    elif seg_bmode == BLEND_SINE:
        factor = calc_sine_factor(middle, pos)
    elif seg_bmode == BLEND_SPHERE_INCREASING:
        factor = calc_sphere_increasing_factor(middle, pos)
    elif seg_bmode == BLEND_SPHERE_DECREASING:
        factor = calc_sphere_decreasing_factor(middle, pos)
    else:
        pass
        # assert False
    lc = seg_left_color
    rc = seg_right_color
    if seg_cmode == RGB:
        r = 255.0 * (lc[0] + (rc[0] - lc[0]) * factor)
        g = 255.0 * (lc[1] + (rc[1] - lc[1]) * factor)
        b = 255.0 * (lc[2] + (rc[2] - lc[2]) * factor)
        a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        a = int(a) % 256
        return r,g,b,a #np.array([r,g,b,a], dtype=np.uint8)
    elif seg_cmode in (HSV_CCW, HSV_CW):
        (lh,ls,lv) = gimp_rgb_to_hsv(lc[0], lc[1], lc[2])
        (rh,rs,rv) = gimp_rgb_to_hsv(rc[0], rc[1], rc[2])

        if seg_cmode == HSV_CCW and lh >= rh:
            rh += 1.0
        if seg_cmode == HSV_CW and lh <= rh:
            lh += 1.0
        h = lh + (rh - lh) * factor
        s = ls + (rs - ls) * factor
        v = lv + (rv - lv) * factor
        if h > 1.0:
            h -= 1.0
        (r,g,b) = gimp_hsv_to_rgb(h,s,v)
        a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
        r = int(r*255.0) % 256
        g = int(g*255.0) % 256
        b = int(b*255.0) % 256
        a = int(a) % 256
        return r,g,b,a #np.array([r,g,b,a], dtype=np.uint8)
    else:
        pass
        # assert False
        return 0,0,0,0 #np.array([0,0,0,0], dtype=np.uint8)

@myjit(typeof_array4(typ_np_cmap, float64, int64))
def lookup_with_transfer(cmap_items, index, solid):
    black = np.array([0,0,0,255], dtype=np.uint8)
    if solid:
        return black
    #return lookup(cmap_items, index)
    r,g,b,a = look33up(cmap_items, index)
    return np.array([r,g,b,a], dtype=np.uint8)

#@jit(typeof(np.zeros((4,),dtype='f8',order='C'))(int64,float64[:]))
#@jit #(int8[:](int64,float64[:]))
@jit(typeof_array4(int64,types.Tuple((float64,float64,float64,float64))))
def lookup_with_dca_nt(solid, colors):
    black = np.array([0,0,0,255], dtype=np.uint8)
    if solid:
        return black
    r = int(255.0 * colors[0]) % 256
    g = int(255.0 * colors[1]) % 256
    b = int(255.0 * colors[2]) % 256
    a = int(255.0 * colors[3]) % 256
    return np.array([r,g,b,a], dtype=np.uint8)

@jit #(typeof_array4(int64,types.Tuple((float64,float64,float64,float64))))
def lookup_with_dca(solid, colors):
    black = np.array([0,0,0,255], dtype=np.uint8)
    if solid:
        return black
    r = int(255.0 * colors[0]) % 256
    g = int(255.0 * colors[1]) % 256
    b = int(255.0 * colors[2]) % 256
    a = int(255.0 * colors[3]) % 256
    return np.array([r,g,b,a], dtype=np.uint8)

dtype_i8i8f8f8 = np.dtype([('i1', 'i8'),('i2', 'i8'),('i3', 'f8'),('i4', 'f8'),('i5', 'f8'),('i6', 'i8')])
dtype_i8f8f8f8f8 = np.dtype([('i1', 'i8'),('i2', 'f8'),('i3', 'f8'),('i4', 'f8'),('i5', 'f8')])

from LiuD import GenLLVM_GFF
cfunc3_ptr = None
g_color_params = None

def CompileLLVM(form0_mod, form1_mod, form2_mod, param0, param1, param2):
    (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset) = (0.0, 0.0, 0.0, 0.0, 0.0)

    for name1, typ1, val1, enum in param1:
        if name1 == '_offset': t__a_cf0_offset = val1
        if name1 == '_density': t__a_cf0_density = val1
        if name1 == 'bailout': t__a_cf0bailout = val1
    for name1, typ1, val1, enum in param2:
        if name1 == '_offset': t__a_cf1_offset = val1
        if name1 == '_density': t__a_cf1_density = val1

    global g_color_params
    g_color_params = (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset)

    global cfunc3_ptr
    theliud3 = GenLLVM_GFF.LLVM_liud(form0_mod, form1_mod, form2_mod, param0, param1, param2)
    cfunc3_ptr = theliud3.cfuncptr
    cfunc3_ptr.savme = theliud3
    # form1 usually continuous_potential
    # form2 usually zero

@myjit #(types.Tuple((int8[:], int64, float64, int64))(complex128, complex128, int64, typ_cmap))
def Mandelbrot_calc_UseLLVM(pixel, zwpixel, maxiter, cmap, checkPeriod, period_tolerance):
    #print 'xxx',pixel, zwpixel, maxiter, cmap
    fUseColors = 0
    colors = [0.0, 0.0, 0.0, 0.0]

    (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset) = g_color_params

    arr = np.zeros(1, dtype=dtype_i8i8f8f8)
    color_arr = np.zeros(1, dtype=dtype_i8f8f8f8f8)
    #print dir(cmap)

    if True:
        n = len(cmap)
        cmap_arr = cmap
    cfunc3_ptr(arr.ctypes.data, pixel.real, pixel.imag, zwpixel.real, zwpixel.imag, maxiter, color_arr.ctypes.data,
               checkPeriod, period_tolerance,
               cmap_arr.ctypes.data, n)
    a1,a2,a3,a4,a5,a6 = arr[0]['i1'], arr[0]['i2'], arr[0]['i3'], arr[0]['i4'], arr[0]['i5'], arr[0]['i6']
    a1 = a1 + len(arr) - len(arr)

    t__h_inside, t__h_numiter, z, indx, solid = a1, a2, complex(a3, a4), a5, a6

    fcolor,colors[0],colors[1],colors[2],colors[3] = color_arr[0]['i1'], color_arr[0]['i2'], color_arr[0]['i3'], color_arr[0]['i4'], color_arr[0]['i5']
    fUseColors = fcolor + len(color_arr) - len(color_arr)

    #colors[0] = 0.0 # I donot know why it always nan or inf

    if t__h_inside == 0:
        t__h_index = t__a_cf0_density * indx + t__a_cf0_offset
    else:
        t__h_index = t__a_cf1_density * indx + t__a_cf1_offset

    iter_ = t__h_numiter
    fate = FATE_INSIDE if t__h_inside != 0 else 0
    dist = t__h_index
    if solid:
        fate |= FATE_SOLID
    if fate & FATE_INSIDE:
        iter_ = -1
    if fUseColors:
        fate |= FATE_DIRECT
        #pixel_ = lookup_with_dca(solid, colors)
        pixel_ = lookup_with_dca_nt(solid, (colors[0],colors[1],colors[2],colors[3]))
    else:
        pixel_ = lookup_with_transfer(cmap_arr, dist, solid)
    #print 'fff',pixel_, fate, dist, iter_
    # fff [ 70  72 230 255] 0 0.00330332703674 0

    return (pixel_, fate, dist, iter_)

@myjit #(types.Tuple((int8[:], int64, float64, int64))(typ_cmap, float64[:], int64))
def calc_pf_UseLLVM(cmap, params, nIters, checkPeriod, period_tolerance):
    pixel = complex(params[0], params[1])
    zwpixel = complex(params[2], params[3])

    return Mandelbrot_calc_UseLLVM(pixel, zwpixel, nIters, cmap, checkPeriod, period_tolerance)

@jit(float64(complex128))
def abs2(c):
    return c.imag * c.imag + c.real * c.real

@myjit(none(typ_im_info, typ_np_cmap))
def recolor(selfii, cmap):
    dist = selfii.index
    fate = selfii.fate
    solid = 0
    inside = 0
    if fate & FATE_DIRECT:
        return
    if fate & FATE_SOLID:
        solid = 1
    if fate & FATE_INSIDE:
        inside = 1
    pixel = lookup_with_transfer(cmap, dist, solid)
    selfii.set_pixel(pixel)

@myjit#(none(typ_stfw, int64, int64, int64, int64))
def do_pixel(stfw, x, y, w, h):
    (self_cmap, im, ff) = stfw
    ii = im_info(im)
    ii.init_fate(x,y)
    if ii.fate == FATE_UNKNOWN:
        (ff_topleft, ff_deltax, ff_deltay, ff_maxiter, periodicity, period_tolerance) = ff
        pos = ff_topleft + ff_deltax * x + ff_deltay * y
        checkPeriod = im.periodGuess(periodicity, ff_maxiter)
        (pixel, fate, index, iter_) = calc_pf_UseLLVM(self_cmap, pos, ff_maxiter, checkPeriod, period_tolerance)
        im.periodSet(iter_)
        ii2 = im_info(im)
        ii2.pixel = pixel; ii2.fate = fate; ii2.index = index; ii2.iter = iter_
        ii2.writeback(x,y)
        ii2.rectangle(x,y,w,h)
    else:
        ii.init(x,y)
        recolor(ii, self_cmap)
        ii.rectangle(x,y,w,h)

@myjit #(none(typ_stfw, int64, int64, int64))
def row(stfw, x, y, n):
    for i in range(n):
        do_pixel(stfw,x+i, y, 1, 1)

@myjit #(none(typ_stfw, int64, int64, int64, int64))
def qbox_row(stfw, w, y, rsize, drawsize):
    x = 0
    while x < w-rsize:
        do_pixel(stfw,x,y,drawsize,drawsize)
        x += rsize-1
    y2 = y
    while y2 < y + rsize:
        row(stfw,x,y2,w-x)
        y2 += 1

@myjit #(none(typ_stfw, int64, int64, int64))
def do_box(stfw, x, y, rsize):
    (_, im, _) = stfw
    bFlat = True
    iter = im.getIter(x,y)
    pcol = RGB2INT(im,x,y)
    for x2 in range(x, x+rsize):
        do_pixel(stfw,x2,y,1,1)
        bFlat = isTheSame(im,bFlat,iter,pcol,x2,y)
        do_pixel(stfw,x2,y+rsize-1,1,1)
        bFlat = isTheSame(im,bFlat,iter,pcol,x2,y+rsize-1)
    for y2 in range(y, y+rsize):
        do_pixel(stfw,x,y2,1,1)
        bFlat = isTheSame(im,bFlat,iter,pcol,x,y2)
        do_pixel(stfw,x+rsize-1,y2,1,1)
        bFlat = isTheSame(im,bFlat,iter,pcol,x+rsize-1,y2)
    if bFlat:
        ii = im_info(im); ii.init(x,y)
        ii.rectangle_with_iter(x+1,y+1,rsize-2,rsize-2)
    else:
        if rsize > 4:
            half_size = rsize / 2
            do_box(stfw,x,y,half_size)
            do_box(stfw,x+half_size,y,half_size)
            do_box(stfw,x,y+half_size, half_size)
            do_box(stfw,x+half_size,y+half_size,half_size)
        else:
            for y2 in range(y+1,y+rsize-1):
                row(stfw,x+1,y2,rsize-2)

@myjit #(none(typ_stfw, int64, int64, int64))
def box_row(stfw, w, y, rsize):
    x = 0
    while x < w-rsize:
        do_box(stfw,x,y,rsize)
        x += rsize - 1
    for y2 in range(y, y+rsize):
        row(stfw,x,y2,w-x)

@myjit(int64(typ_pfo_p))
def test_param1(self_pfo_p):
    return 0

@myjit(int64(typ_cmap))
def test_param2(self_cmap):
    return 0

#@myjit(int64(typeof_Image))
#def test_param3(im):
#    return 0

@myjit(int64(int64))
def test_param4(fnno):
    return 0


@myjit(none(typ_ff))
def test_param5(ff):
    pass


@myjit #(none(typ_stfw))
def draw_8(stfw):
    (self_cmap, im, _) = stfw

    rsize = 16; drawsize = 16
    xsize = im.Xres(); ysize = im.Yres()
    w = xsize; h = ysize
    y = 0
    while y < h - rsize:
        qbox_row(stfw,w,y,rsize,drawsize)
        y += rsize
    while y < h:
        row(stfw,0,y,w)
        y += 1
    y = 0
    while y < h - rsize:
        box_row(stfw,w,y,rsize)
        y += rsize

@myjit(float64[:](float64,float64,float64))
def rotXY(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([c, -s, zero, zero,
        s, c, zero, zero,
        zero, zero, one, zero,
        zero, zero, zero, one], dtype=np.float64) #.reshape((4,4))

@myjit(float64[:](float64,float64,float64))
def rotXZ(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([c, zero, s, zero,
        zero, one, zero, zero,
        -s, zero, c, zero,
        zero, zero, zero, one], dtype=np.float64) #.reshape((4,4))
@myjit(float64[:](float64,float64,float64))
def rotXW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([c, zero, zero, s,
        zero, one, zero, zero,
        zero, zero, one, zero,
        -s, zero, zero, c], dtype=np.float64) #.reshape((4,4))
@myjit(float64[:](float64,float64,float64))
def rotYZ(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([one, zero, zero, zero,
        zero, c, -s, zero,
        zero, s, c, zero,
        zero, zero, zero, one], dtype=np.float64) #.reshape((4,4))
@myjit(float64[:](float64,float64,float64))
def rotYW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([one, zero, zero, zero,
        zero, c, zero, s,
        zero, zero, one, zero,
        zero, -s, zero, c], dtype=np.float64) #.reshape((4,4))
@myjit(float64[:](float64,float64,float64))
def rotZW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array([one, zero, zero, zero,
        zero, one, zero, zero,
        zero, zero, c, -s,
        zero, zero, s, c], dtype=np.float64) #.reshape((4,4))

@myjit(typeof(np.zeros((16,), dtype='f8', order='C'))(float64[:],float64[:]))
def matmult(a,b):
    return np.array([a[0]*b[0]+a[1]*b[4]+a[2]*b[8]+a[3]*b[12],
                     a[0]*b[1]+a[1]*b[5]+a[2]*b[9]+a[3]*b[13],
                     a[0]*b[2]+a[1]*b[6]+a[2]*b[10]+a[3]*b[14],
                     a[0]*b[3]+a[1]*b[7]+a[2]*b[11]+a[3]*b[15],

                     a[4]*b[0]+a[5]*b[4]+a[6]*b[8]+a[7]*b[12],
                     a[4]*b[1]+a[5]*b[5]+a[6]*b[9]+a[7]*b[13],
                     a[4]*b[2]+a[5]*b[6]+a[6]*b[10]+a[7]*b[14],
                     a[4]*b[3]+a[5]*b[7]+a[6]*b[11]+a[7]*b[15],

                     a[8]*b[0]+a[9]*b[4]+a[10]*b[8]+a[11]*b[12],
                     a[8]*b[1]+a[9]*b[5]+a[10]*b[9]+a[11]*b[13],
                     a[8]*b[2]+a[9]*b[6]+a[10]*b[10]+a[11]*b[14],
                     a[8]*b[3]+a[9]*b[7]+a[10]*b[11]+a[11]*b[15],

                     a[12]*b[0]+a[13]*b[4]+a[14]*b[8]+a[15]*b[12],
                     a[12]*b[1]+a[13]*b[5]+a[14]*b[9]+a[15]*b[13],
                     a[12]*b[2]+a[13]*b[6]+a[14]*b[10]+a[15]*b[14],
                     a[12]*b[3]+a[13]*b[7]+a[14]*b[11]+a[15]*b[15],
                     ])

@myjit #(typeof(np.zeros((4,4), dtype='f8', order='C'))(float64[:]))
def rotated_matrix(params):
    id = (np.identity(4) * params[MAGNITUDE]).reshape(16)
    m12 = rotXY(params[XYANGLE], 1.0, 0.0)
    m12 = matmult(id, m12)
    m23 = rotXZ(params[XZANGLE], 1.0, 0.0)
    m = matmult(m12, m23)
    m23 = rotXW(params[XWANGLE], 1.0, 0.0)
    m = matmult(m, m23)
    m23 = rotYZ(params[YZANGLE], 1.0, 0.0)
    m = matmult(m, m23)
    m23 = rotYW(params[YWANGLE], 1.0, 0.0)
    m = matmult(m, m23)
    m23 = rotZW(params[ZWANGLE], 1.0, 0.0)
    m = matmult(m, m23)
    return m.reshape((4,4))

@myjit #(types.Tuple((float64[:],float64[:],float64[:]))(typeof_Image,float64[:]))
def GetPos_delta(im, params):
    xtotalsize = im.totalXres()
    ytotalsize = im.totalYres()
    xoffset = im.Xoffset()
    yoffset = im.Yoffset()

    center = np.array([params[XCENTER], params[YCENTER], params[ZCENTER], params[WCENTER]])
    #print 'mycenter', center

    rot = rotated_matrix(params)

    rot = rot / xtotalsize
    #print 'myrot', rot

    self_deltax = rot[VX] #.getA1()
    self_deltay = -rot[VY] #.getA1()

    delta_aa_x = self_deltax / 2.0
    delta_aa_y = self_deltay / 2.0

    topleft = center - self_deltax * xtotalsize / 2.0 - self_deltay * ytotalsize / 2.0

    topleft += xoffset * self_deltax;
    topleft += yoffset * self_deltay;

    topleft += delta_aa_x + delta_aa_y;

    return self_deltax, self_deltay, topleft

def draw(image, outputfile, formuName, initparams, params, cmap,
         maxiter, periodicity, period_tolerance):

    pfcls = (params, cmap, image._img,
             maxiter, periodicity, period_tolerance)

    for (xoff,yoff,xres,yres) in image.get_tile_list():
        calc_7(pfcls, xoff, yoff, xres, yres)


Cmap_spec = [
    ('m_1', typ_cmap),
]

@myjitclass(Cmap_spec)
class ClassCmap(object):
    def __init__(self, items):
        self.m_1 = items

typ36 = types.Tuple((float64, float64, float64, int64, int64,
                     types.Tuple((float64, float64, float64, float64)),
                     types.Tuple((float64, float64, float64, float64))
                     ))
tem32 = [(0.0,0.0,0.0,0,0,(0.0,0.0,0.0,0.0),(0.0,0.0,0.0,0.0))]
tem33 = ClassCmap(tem32)
typ_ccmap = typeof(tem33)
del tem33
del tem32

@numba.cfunc(types.Tuple((byte, byte, byte, byte))(float64, types.CPointer(typ36), int64))
def lookup_cfunc(input_index, ptr_cmap, n):
    index = 1.0 if input_index == 1.0 else input_index - int(input_index)
    i = n - n
    while i < n:
        (seg_left, seg_right, seg_mid, seg_bmode, seg_cmode, seg_left_color, seg_right_color) = ptr_cmap[i]
        if index <= seg_right:
            break
        i += 1

    seg_len = seg_right - seg_left
    EPSILON = 1e-10
    if seg_len < EPSILON:
        middle = 0.5
        pos = 0.5
    else:
        middle = (seg_mid - seg_left) / seg_len
        pos = (index - seg_left) / seg_len
    if seg_bmode == BLEND_LINEAR:
        factor = calc_linear_factor(middle, pos)
    elif seg_bmode == BLEND_CURVED:
        factor = calc_curved_factor(middle, pos)
    elif seg_bmode == BLEND_SINE:
        factor = calc_sine_factor(middle, pos)
    elif seg_bmode == BLEND_SPHERE_INCREASING:
        factor = calc_sphere_increasing_factor(middle, pos)
    elif seg_bmode == BLEND_SPHERE_DECREASING:
        factor = calc_sphere_decreasing_factor(middle, pos)
    else:
        pass
        # assert False
    lc = seg_left_color
    rc = seg_right_color
    if seg_cmode == RGB:
        r = 255.0 * (lc[0] + (rc[0] - lc[0]) * factor)
        g = 255.0 * (lc[1] + (rc[1] - lc[1]) * factor)
        b = 255.0 * (lc[2] + (rc[2] - lc[2]) * factor)
        a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        a = int(a) % 256
        return r,g,b,a #np.array([r,g,b,a], dtype=np.uint8)
    elif seg_cmode in (HSV_CCW, HSV_CW):
        (lh,ls,lv) = gimp_rgb_to_hsv(lc[0], lc[1], lc[2])
        (rh,rs,rv) = gimp_rgb_to_hsv(rc[0], rc[1], rc[2])

        if seg_cmode == HSV_CCW and lh >= rh:
            rh += 1.0
        if seg_cmode == HSV_CW and lh <= rh:
            lh += 1.0
        h = lh + (rh - lh) * factor
        s = ls + (rs - ls) * factor
        v = lv + (rv - lv) * factor
        if h > 1.0:
            h -= 1.0
        (r,g,b) = gimp_hsv_to_rgb(h,s,v)
        a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
        r = int(r*255.0) % 256
        g = int(g*255.0) % 256
        b = int(b*255.0) % 256
        a = int(a) % 256
        return r,g,b,a #np.array([r,g,b,a], dtype=np.uint8)
    else:
        pass
        # assert False
        return 0,0,0,0 #np.array([0,0,0,0], dtype=np.uint8)

@myjit(float64(float64, float64, float64))
def rgb_component(n1, n2, hue):
    if hue > 6.0:
        hue -= 6.0
    elif hue < 0.0:
        hue += 6.0
    if hue < 1.0:
        return n1 + (n2 - n1)*hue
    if hue < 3.0:
        return n2
    if hue < 4.0:
        return n1 + (n2 - n1)*(4.0 - hue)
    return n1


@numba.cfunc(types.Tuple((float64,float64,float64))(float64, float64, float64))
def hsl_to_rgb(h, s, l):
    if s == 0.0:
        return (l, l, l)
    if l <= 0.5:
        n2 = l * (1.0 + s)
    else:
        n2 = l + s - l*s

    n1 = 2.0 * l - n2

    r = rgb_component(n1, n2, h + 2.0)
    g = rgb_component(n1, n2, h)
    b = rgb_component(n1, n2, h - 2.0)

    return (r, g, b)

def compose(color1, color2, oprate):
    rate = color2.a * oprate
    c1 = color1 * (1.0 - rate)
    c2 = color2 * rate
    result = c1 + c2
    result.a = color1.a
    return result