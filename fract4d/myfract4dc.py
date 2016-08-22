import numpy as np
# import png  # pypng (0.0.18)
import numba
from numba import jit, jitclass, types, typeof, int64, float64, complex64 # 0.27.0
import mycalc

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
]

@jitclass(Image_spec)
class Image(object):
    def __init__(self):
        self.m_Xres = self.m_Yres = 0
        self.m_totalXres = self.m_totalYres = 0
        self.m_xoffset = self.m_yoffset = 0
        self.buffer = np.zeros(0,dtype=np.uint8) #None
        self.iter_buf = np.zeros(0,dtype=np.int64) #None
        self.fate_buf = np.zeros(0,dtype=np.uint8) #None
        self.index_buf = np.zeros(0,dtype=np.float64) #None

    def Xres(self): return self.m_Xres
    def Yres(self): return self.m_Yres
    def totalXres(self): return self.m_totalXres
    def totalYres(self): return self.m_totalYres
    def Xoffset(self): return self.m_xoffset
    def Yoffset(self): return self.m_yoffset
    def row_length(self): return self.Xres() * 3
    def bytes(self): return self.row_length() * self.m_Yres

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

def cmap_from_pyobject(segs):
    n = len(segs)
    cmap_items = [] # ColorMap(n)
    for i in range(n):
        the = gradient_item_t()
        left = segs[i].left
        right = segs[i].right
        mid = segs[i].mid
        cmode = segs[i].cmode
        bmode = segs[i].bmode
        left_col = segs[i].left_color
        right_col = segs[i].right_color
        the.set(left, right, mid,
                 left_col, right_col,
                 bmode, cmode)
        cmap_items.append(the)
    return cmap_items

def calc_7(pfcls, xoff, yoff, xres, yres):
    (self_formuNameNo, self_params, self_pfo_p, self_cmap, self_maxiter, im) = pfcls

    xtotalsize = im.totalXres()
    ytotalsize = im.totalYres()
    im.set_resolution(xres, yres, xtotalsize, ytotalsize)
    im.set_offset(xoff, yoff)

    (ff_deltax, ff_deltay, ff_topleft) = GetPos_delta(im, self_params)

    ff = (ff_topleft, ff_deltax, ff_deltay, self_maxiter)

    stfw = (self_pfo_p, self_cmap, im, self_formuNameNo, ff)

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

@jit
def qbox_row(stfw, w, y, rsize, drawsize):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw
    x = 0
    while x < w-rsize:
        do_pixel(stfw,x,y,drawsize,drawsize)
        x += rsize-1
    y2 = y
    while y2 < y + rsize:
        row(stfw,x,y2,w-x)
        y2 += 1

@jit
def do_pixel(stfw, x, y, w, h):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw
    ii = im_info(im)
    ii.init_fate(x,y)
    if ii.fate == FATE_UNKNOWN:
        (ff_topleft, ff_deltax, ff_deltay, ff_maxiter) = ff
        pos = ff_topleft + ff_deltax * x + ff_deltay * y
        (pixel, fate, index, iter_) = calc_pf(self_pfo_p, self_cmap, self_formuNameNo, pos, ff_maxiter)
        ii2 = im_info(im)
        ii2.pixel = pixel; ii2.fate = fate; ii2.index = index; ii2.iter = iter_
        ii2.writeback(x,y)
        ii2.rectangle(x,y,w,h)
    else:
        ii.init(x,y)
        recolor(ii, self_cmap)
        ii.rectangle(x,y,w,h)

@jit
def row(stfw, x, y, n):
    for i in range(n):
        do_pixel(stfw,x+i, y, 1, 1)

@jit
def box_row(stfw, w, y, rsize):
    x = 0
    while x < w-rsize:
        do_box(stfw,x,y,rsize)
        x += rsize - 1
    for y2 in range(y, y+rsize):
        row(stfw,x,y2,w-x)
@jit
def RGB2INT(stfw,x,y):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw
    pixel = im.get(x,y)
    return Pixel2INT(pixel)
@jit
def do_box(stfw, x, y, rsize):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw
    bFlat = True
    iter = im.getIter(x,y)
    pcol = RGB2INT(stfw,x,y)
    for x2 in range(x, x+rsize):
        do_pixel(stfw,x2,y,1,1)
        bFlat = isTheSame(stfw,bFlat,iter,pcol,x2,y)
        do_pixel(stfw,x2,y+rsize-1,1,1)
        bFlat = isTheSame(stfw,bFlat,iter,pcol,x2,y+rsize-1)
    for y2 in range(y, y+rsize):
        do_pixel(stfw,x,y2,1,1)
        bFlat = isTheSame(stfw,bFlat,iter,pcol,x,y2)
        do_pixel(stfw,x+rsize-1,y2,1,1)
        bFlat = isTheSame(stfw,bFlat,iter,pcol,x+rsize-1,y2)
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
@jit
def isTheSame(stfw, bFlat, targetIter, targetCol, x, y):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw
    if not bFlat:
        return False
    if im.getIter(x,y) != targetIter:
        return False
    if RGB2INT(stfw,x,y) != targetCol:
        return False
    return True

@jit
def Pixel2INT(pixel):
    r,g,b,a = pixel
    return (r << 16) | (g << 8) | b

@jit
def calc_pf(pfo_p, cmap, formuNameNo, params, nIters):
    cf0cf1, values = pfo_p
    pixel = complex(params[0], params[1])
    zwpixel = complex(params[2], params[3])

    return Mandelbrot_calc(values, pixel, zwpixel, nIters, cf0cf1, formuNameNo, cmap)


@jit # (nopython=True)
def Mandelbrot_calc(param_values, pixel, zwpixel, maxiter, cf0cf1, formuNameNo, cmap):
    fUseColors = 0
    colors = [0.0, 0.0, 0.0, 0.0]

    (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset) = cf0cf1

    if formuNameNo == 1: # 'Mandelbrot':
        t__a_fbailout = param_values[0]
        t__h_inside, t__h_numiter, z = mycalc.Mandelbrot_1(t__a_fbailout, pixel, zwpixel, maxiter)
    elif formuNameNo == 2: # 'CGNewton3':
        p1_tuple = param_values[0]
        p1 = complex(p1_tuple[0], p1_tuple[1])
        t__h_inside, t__h_numiter, z = mycalc.CGNewton3_1(p1, pixel, maxiter)
    else: # if formuNameNo == 3: # 'Cubic Mandelbrot':
        t__a_fbailout = param_values[0]
        t__a_fa = param_values[1]
        fa = complex(t__a_fa[0], t__a_fa[1])
        t__h_inside, t__h_numiter, z = mycalc.Cubic_Mandelbrot_1(fa, t__a_fbailout, pixel, zwpixel, maxiter)

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
    # return fUseColors, colors, solid, dist, iter_, fate
    if fUseColors:
        pixel_ = lookup_with_dca(solid, colors)
    else:
        pixel_ = lookup_with_transfer(cmap, dist, solid)
    return (pixel_, fate, dist, iter_)

@jit(float64(complex64))
def abs2(c):
    return c.imag * c.imag + c.real * c.real


tem33 = Image()

ii_spec = [
    #('im', typeof(Image)),
    ('im', typeof(tem33)),
    ('index', float64),
    ('iter', int64),
    ('fate', numba.uint8),
    ('pixel', numba.uint8[:]),
]
del tem33

@jitclass(ii_spec)
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

@jit
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

def GetPos_delta(im, params):
    xtotalsize = im.totalXres()
    ytotalsize = im.totalYres()
    xoffset = im.Xoffset()
    yoffset = im.Yoffset()

    center = np.asarray([params[XCENTER], params[YCENTER], params[ZCENTER], params[WCENTER]])
    #print 'mycenter', center

    rot = rotated_matrix(params)

    rot = rot / xtotalsize
    #print 'myrot', rot

    self_deltax = rot[VX].getA1()
    self_deltay = -rot[VY].getA1()

    delta_aa_x = self_deltax / 2.0
    delta_aa_y = self_deltay / 2.0

    topleft = center - self_deltax * xtotalsize / 2.0 - self_deltay * ytotalsize / 2.0

    topleft += xoffset * self_deltax;
    topleft += yoffset * self_deltay;

    topleft += delta_aa_x + delta_aa_y;

    return self_deltax, self_deltay, topleft

@jit
def draw_8(stfw):
    (self_pfo_p, self_cmap, im, self_formuNameNo, ff) = stfw

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

gradient_item_t_spec = [
    ('left', float64),
    ('right', float64),
    ('bmode', int64),
    ('cmode', int64),
    ('mid', float64),
    ('left_color', float64[:]),
    ('right_color', float64[:]),
]

@jitclass(gradient_item_t_spec)
class gradient_item_t(object):
    def __init__(self):
        self.left = 0.0
        self.right = 0.0
        self.mid = 0.0
        self.left_color = np.zeros(0,dtype=np.float64)
        self.right_color = np.zeros(0,dtype=np.float64)
        self.bmode = BLEND_LINEAR
        self.cmode = RGB
    def set(self, left, right, mid, left_col, right_col, bmode, cmode):
        self.left = left
        self.right = right
        self.mid = mid
        #print 'left_col', type(left_col), left_col
        #print 'right_col', type(right_col), right_col
        n = len(left_col)
        leftc = np.zeros(n,dtype=np.float64)
        for j in range(n):
            leftc[j] = left_col[j]
        self.left_color = leftc

        n = len(right_col)
        rightc = np.zeros(n,dtype=np.float64)
        for j in range(n):
            rightc[j] = right_col[j]
        self.right_color = rightc

        #self.items[i].left_color = left_col
        #self.items[i].right_color = right_col
        self.bmode = bmode
        self.cmode = cmode

@jit
def lookup_with_transfer(cmap_items, index, solid):
    black = np.array([0,0,0,255], dtype=np.uint8)
    if solid:
        return black
    return lookup(cmap_items, index)
@jit
def lookup(cmap_items, input_index):
    self_items = cmap_items
    self_ncolors = len(cmap_items)
    index = 1.0 if input_index == 1.0 else input_index - int(input_index)
    i = grad_find(index, self_items, self_ncolors)
    seg = self_items[i]
    seg_len = seg.right - seg.left
    if seg_len < EPSILON:
        middle = 0.5
        pos = 0.5
    else:
        middle = (seg.mid - seg.left) / seg_len
        pos = (index - seg.left) / seg_len
    if seg.bmode == BLEND_LINEAR:
        factor = calc_linear_factor(middle, pos)
    elif seg.bmode == BLEND_CURVED:
        factor = calc_curved_factor(middle, pos)
    elif seg.bmode == BLEND_SINE:
        factor = calc_sine_factor(middle, pos)
    elif seg.bmode == BLEND_SPHERE_INCREASING:
        factor = calc_sphere_increasing_factor(middle, pos)
    elif seg.bmode == BLEND_SPHERE_DECREASING:
        factor = calc_sphere_decreasing_factor(middle, pos)
    else:
        pass
        # assert False
    lc = seg.left_color
    rc = seg.right_color
    if seg.cmode == RGB:
        r = 255.0 * (lc[0] + (rc[0] - lc[0]) * factor)
        g = 255.0 * (lc[1] + (rc[1] - lc[1]) * factor)
        b = 255.0 * (lc[2] + (rc[2] - lc[2]) * factor)
        a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        a = int(a) % 256
        return np.array([r,g,b,a], dtype=np.uint8)
    elif seg.cmode in (HSV_CCW, HSV_CW):
        (lh,ls,lv) = gimp_rgb_to_hsv(lc[0], lc[1], lc[2])
        (rh,rs,rv) = gimp_rgb_to_hsv(rc[0], rc[1], rc[2])

        if seg.cmode == HSV_CCW and lh >= rh:
            rh += 1.0
        if seg.cmode == HSV_CW and lh <= rh:
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
        return np.array([r,g,b,a], dtype=np.uint8)
    else:
        pass
        # assert False
        return np.array([0,0,0,0], dtype=np.uint8)

def lookup_with_dca(solid, colors):
    black = np.array([0,0,0,255], dtype=np.uint8)
    if solid:
        return black
    r = int(255.0 * colors[0]) % 256
    g = int(255.0 * colors[1]) % 256
    b = int(255.0 * colors[2]) % 256
    a = int(255.0 * colors[3]) % 256
    return np.array([r,g,b,a], dtype=np.uint8)

EPSILON = 1e-10

def rgb_to_hsv(r,g,b):
    min_ = min(r,g,b)
    max_ = max(r,g,b)
    v = max_
    delta = max_ - min_
    s = 0.0 if max_ == 0.0 else delta / max_
    if s == 0.0:
        h = 0
        return (h,s,v)
    if r == max_:
        h = (g - b) / delta
    elif g == max_:
        h = 2 + (b - r) / delta
    else:
        h = 4 + (r - g) / delta
    if h < 0:
        h += 6.0
    return (h, s, v)

def gimp_rgb_to_hsv(r,g,b):
    (h,s,v) = rgb_to_hsv(r,g,b)
    return (h / 6.0, s, v)

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
        assert False

def gimp_hsv_to_rgb(h,s,v):
    return hsv_to_rgb(h * 6.0, s, v)

def calc_sphere_decreasing_factor(middle, pos):
    pos = calc_linear_factor(middle, pos)
    return 1.0 - math.sqrt(1.0 - pos * pos)

def calc_sphere_increasing_factor(middle, pos):
    pos = calc_linear_factor(middle, pos) - 1.0
    return math.sqrt(1.0 - pos * pos)

def calc_sine_factor(middle, pos):
    pos = calc_linear_factor(middle, pos)
    return (math.sin((-math.pi / 2.0) + math.pi * pos) + 1.0) / 2.0

def calc_curved_factor(middle, pos):
    middle = max(middle, EPSILON)
    return math.pow(pos, math.log(0.5)) / math.log(middle)

def calc_linear_factor(middle, pos):
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

def grad_find(index, items, ncolors):
    for i in range(ncolors):
        if index <= items[i].right:
            return i
    return -1

import math
def rotXY(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [c, -s, zero, zero],
        [s, c, zero, zero],
        [zero, zero, one, zero],
        [zero, zero, zero, one]
    ])
def rotXZ(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [c, zero, s, zero],
        [zero, one, zero, zero],
        [-s, zero, c, zero],
        [zero, zero, zero, one]
    ])
def rotXW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [c, zero, zero, s],
        [zero, one, zero, zero],
        [zero, zero, one, zero],
        [-s, zero, zero, c]
    ])
def rotYZ(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [one, zero, zero, zero],
        [zero, c, -s, zero],
        [zero, s, c, zero],
        [zero, zero, zero, one]
    ])
def rotYW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [one, zero, zero, zero],
        [zero, c, zero, s],
        [zero, zero, one, zero],
        [zero, -s, zero, c]
    ])
def rotZW(theta, one, zero):
    c = math.cos(theta)
    s = math.sin(theta)
    return np.matrix([
        [one, zero, zero, zero],
        [zero, one, zero, zero],
        [zero, zero, c, -s],
        [zero, zero, s, c]
    ])

def rotated_matrix(params):
    id = np.identity(4) * params[MAGNITUDE]
    id2 = id * rotXY(params[XYANGLE], 1.0, 0.0) \
        * rotXZ(params[XZANGLE], 1.0, 0.0) \
        * rotXW(params[XWANGLE], 1.0, 0.0) \
        * rotYZ(params[YZANGLE], 1.0, 0.0) \
        * rotYW(params[YWANGLE], 1.0, 0.0) \
        * rotZW(params[ZWANGLE], 1.0, 0.0)
    return id2

class s_param:
    pass
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

def parse_params_to_dict(params):
    (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset) = (0.0, 0.0, 0.0, 0.0, 0.0)
    names = []
    values = []
    for param, var in params:
        name = var.cname
        if name == 't__a_cf0bailout': t__a_cf0bailout = param
        elif name == 't__a_cf0_density': t__a_cf0_density = param
        elif name == 't__a_cf0_offset': t__a_cf0_offset = param
        elif name == 't__a_cf1_density': t__a_cf1_density = param
        elif name == 't__a_cf1_offset': t__a_cf1_offset = param
        elif name == 't__a__gradient':
            pass
        else:
            names.append(name)
            values.append(param)

    cf0cf1 = (t__a_cf0bailout, t__a_cf0_density, t__a_cf0_offset, t__a_cf1_density, t__a_cf1_offset)
    return (cf0cf1, values)

Flag_My = True

if not Flag_My:
    try:
        import fract4dcgmp as fract4dc
    except ImportError, err:
        import fract4dc


def draw(image, outputfile, formuName, initparams, params, segs, maxiter):
    if Flag_My:

        if formuName == 'Mandelbrot':
            formuNameNo = 1
        elif formuName == 'CGNewton3':
            formuNameNo = 2
        else: # if formuName == 'Cubic Mandelbrot':
            formuNameNo = 3

        pfo_p = parse_params_to_dict(initparams)
        cmap = cmap_from_pyobject(segs)
        _img = image._img

        pfcls = (formuNameNo, params, pfo_p, cmap, maxiter, _img)

        for (xoff,yoff,xres,yres) in image.get_tile_list():
            calc_7(pfcls, xoff, yoff, xres, yres)
        return

    pfunc = fract4dc.pf_load_and_create(outputfile, formuName)

    fract4dc.pf_init(pfunc,params,initparams)

    fract4dc.pf_init2(pfunc, segs, maxiter, image._img)

    for (xoff,yoff,xres,yres) in image.get_tile_list():
        fract4dc.calc(pfo=pfunc, xoff=xoff, yoff=yoff, xres=xres, yres=yres)
