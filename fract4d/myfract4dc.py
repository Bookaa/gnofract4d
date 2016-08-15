import numpy as np

(VX, VY, VZ, VW) = (0,1,2,3)
(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_TOTAL_WIDTH, IMAGE_TOTAL_HEIGHT, IMAGE_XOFFSET, IMAGE_YOFFSET) = (0,1,2,3,4,5)
(XCENTER, YCENTER, ZCENTER, WCENTER, MAGNITUDE, XYANGLE, XZANGLE, XWANGLE, YZANGLE, YWANGLE, ZWANGLE) = (0,1,2,3,4,5,6,7,8,9,10)
(RED, GREEN, BLUE) = (0, 1, 2)
(FATE_UNKNOWN, FATE_SOLID, FATE_DIRECT, FATE_INSIDE) = (255, 0x80, 0x40, 0x20)

class ImageWriter:
    def __init__(self, type_is_png, fp, _img):
        self.fp = fp; self.im = _img

    def save_header(self):
        pass
    def save_tile(self):
        pass
    def save_footer(self):
        pass

N_SUBPIXELS = 4
N_PARAMS = 11

class Image:
    def __init__(self):
        self.m_Xres = self.m_Yres = 0;
        self.m_totalXres = self.m_totalYres = 0;
        self.m_xoffset = self.m_yoffset = 0;
        self.buffer = None #NULL;
        self.iter_buf = None #NULL;
        self.fate_buf = None #NULL;
        self.index_buf = None #NULL;

    def Xres(self): return self.m_Xres
    def Yres(self): return self.m_Yres
    def totalXres(self): return self.m_totalXres
    def totalYres(self): return self.m_totalYres
    def Xoffset(self): return self.m_xoffset
    def Yoffset(self): return self.m_yoffset
    def row_length(self): return self.Xres() * 3
    def bytes(self): return self.row_length() * self.m_Yres

    def delete_buffers(self):
        self.buffer = None #NULL;
        self.iter_buf = None #NULL;
        self.fate_buf = None #NULL;
        self.index_buf = None #NULL;

    def alloc_buffers(self):
        self.buffer = [0] * self.bytes() # char
        self.iter_buf = [0] * (self.m_Xres * self.m_Yres)

        MAX_RECOLOR_SIZE  = 1024*768

        if self.m_Xres * self.m_Yres <= MAX_RECOLOR_SIZE:
            self.index_buf = [0.0] * (self.m_Xres * self.m_Yres * N_SUBPIXELS) # float
            self.fate_buf = [0] * (self.m_Xres * self.m_Yres * N_SUBPIXELS) # unsigned char
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

        if self.buffer and \
           self.m_Xres == x and self.m_Yres == y and \
           self.m_totalXres == totalx and self.m_totalYres == totaly:
           return

        self.m_Xres = x;
        self.m_Yres = y;
        self.m_totalXres = totalx;
        self.m_totalYres = totaly;

        self.delete_buffers();

        self.alloc_buffers()

        pixel = (0,0,0,255)

        for i in range(y):
            for j in range(x):
                self.put(j,i,pixel)
        pass

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
        return (r,g,b,0)
    def getIndex(self,x,y,subpixel):
        n = self.index_of_subpixel(x,y,subpixel)
        return self.index_buf[n]

def cmap_from_pyobject(segs):
    n = len(segs)
    cmap = ColorMap(n)
    for i in range(n):
        left = segs[i].left
        right = segs[i].right
        mid = segs[i].mid
        cmode = segs[i].cmode
        bmode = segs[i].bmode
        left_col = segs[i].left_color
        right_col = segs[i].right_color
        cmap.set(i, left, right, mid,
                 left_col, right_col,
                 bmode, cmode)
    return cmap

class Empty:
    pass
class MyFract4dc:
    (IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_TOTAL_WIDTH, IMAGE_TOTAL_HEIGHT, IMAGE_XOFFSET, IMAGE_YOFFSET) = (0,1,2,3,4,5)

    def image_create(self, xsize, ysize, txsize, tysize):
        img = Image()
        img.set_resolution(xsize, ysize, txsize, tysize)
        return img
        #_img = fract4dc.image_create(xsize, ysize, txsize, tysize)
    def pf_load_and_create(self, outputfile):
        import mycalc

        # import fract4dc
        # pfunc = fract4dc.pf_load_and_create(outputfile)
        pfh = Empty()
        pfh.pfo = mycalc.pf_new()
        pfh.cmap = None
        pfh._img = None
        return pfh
    def pf_init(self, pfunc, params, initparams):
        import mycalc

        the = pfunc
        the.params = params
        the.initparams = initparams

        s_params = mycalc.parse_params(initparams)
        mycalc.init(the, params, s_params)

    def pf_init2(self, pfunc, segs, maxiter, _img):
        the = pfunc
        the.cmap = cmap_from_pyobject(segs)
        the.maxiter = maxiter
        the._img = _img
    def image_dims(self, _img):
        xsize = _img.Xres()
        ysize = _img.Yres()
        xoffset = _img.Xoffset()
        yoffset = _img.Yoffset()
        xtotalsize = _img.totalXres()
        ytotalsize = _img.totalYres()
        return (xsize, ysize, xtotalsize, ytotalsize, xoffset, yoffset)
    def calc(self, **ww):
        the = ww['pfo']
        #pfunc = the.pfunc
        xoff = ww['xoff']
        yoff = ww['yoff']
        xres = ww['xres']
        yres = ww['yres']
        im = the._img

        xtotalsize = im.totalXres()
        ytotalsize = im.totalYres()
        im.set_resolution(xres, yres, xtotalsize, ytotalsize)
        im.set_offset(xoff, yoff)

        #params = [0.0] * N_PARAMS # double
        #parse_posparams(the.params, params)
        # import mycalc
        # mycalc.calc(pfo=the.pfo, xoff=xoff, yoff=yoff, xres=xres, yres=yres)
        calc_4(the.params, the.maxiter, the.pfo, the.cmap, the._img)

        #assert False
        # fract4dc.calc(pfo=pfunc, xoff=xoff, yoff=yoff, xres=xres, yres=yres)
    def image_save_all(self, _img, fp):
        FILE_TYPE_PNG = 1
        iw = ImageWriter(FILE_TYPE_PNG, fp, _img)
        iw.save_header()
        iw.save_tile()
        iw.save_footer()

class STFractWorker:
    def __init__(self, pfo, cmap, im):
        self.pfo = pfo
        self.cmap = cmap
        self.im = im
        self.ff = None
    def qbox_row(self, w, y, rsize, drawsize):
        x = 0
        while x < w-rsize:
            self.pixel(x,y,drawsize,drawsize)
            x += rsize-1
        y2 = y
        while y2 < y + rsize:
            self.row(x,y2,w-x)
            y2 += 1
    def pixel(self, x, y, w, h):
        pf = pointFunc(self.pfo, self.cmap)
        ii = im_info(self.im)
        ii.init_fate(x,y)
        if ii.fate == FATE_UNKNOWN:
            pos = self.ff.topleft + self.ff.deltax * x + self.ff.deltay * y
            ii2 = im_info(self.im)
            pf.calc_pf(pos, self.ff.maxiter, ii2)
            ii2.writeback(x,y)
            ii2.rectangle(x,y,w,h)
        else:
            ii.init(x,y)
            pf.recolor(ii)
            ii.rectangle(x,y,w,h)
    def row(self, x, y, n):
        for i in range(n):
            self.pixel(x+i, y, 1, 1)
    def box_row(self, w, y, rsize):
        x = 0
        while x < w-rsize:
            self.box(x,y,rsize)
            x += rsize - 1
        for y2 in range(y, y+rsize):
            self.row(x,y2,w-x)
    def RGB2INT(self,x,y):
        pixel = self.im.get(x,y)
        return Pixel2INT(pixel)
    def box(self, x, y, rsize):
        bFlat = True
        iter = self.im.getIter(x,y)
        pcol = self.RGB2INT(x,y)
        for x2 in range(x, x+rsize):
            self.pixel(x2,y,1,1)
            bFlat = self.isTheSame(bFlat,iter,pcol,x2,y)
            self.pixel(x2,y+rsize-1,1,1)
            bFlat = self.isTheSame(bFlat,iter,pcol,x2,y+rsize-1)
        for y2 in range(y, y+rsize):
            self.pixel(x,y2,1,1)
            bFlat = self.isTheSame(bFlat,iter,pcol,x,y2)
            self.pixel(x+rsize-1,y2,1,1)
            bFlat = self.isTheSame(bFlat,iter,pcol,x+rsize-1,y2)
        if bFlat:
            ii = im_info(self.im); ii.init(x,y)
            ii.rectangle_with_iter(x+1,y+1,rsize-2,rsize-2)
        else:
            if rsize > 4:
                half_size = rsize / 2
                self.box(x,y,half_size)
                self.box(x+half_size,y,half_size)
                self.box(x,y+half_size, half_size)
                self.box(x+half_size,y+half_size,half_size)
            else:
                for y2 in range(y+1,y+rsize-1):
                    self.row(x+1,y2,rsize-2)

    def isTheSame(self, bFlat, targetIter, targetCol, x, y):
        if not bFlat:
            return False
        if self.im.getIter(x,y) != targetIter:
            return False
        if self.RGB2INT(x,y) != targetCol:
            return False
        return True
def Pixel2INT(pixel):
    r,g,b,a=pixel
    r = int(r) % 255
    g = int(g) % 255
    b = int(b) % 255
    return (r << 16) | (g << 8) | b

class pointFunc:
    def __init__(self, pfo, cmap):
        self.pfo = pfo
        self.cmap = cmap
    def calc_pf(self, params, nIters, ii):
        import mycalc
        fUseColors, colors, solid, dist, iter_, fate = mycalc.calc(self.pfo, params, nIters)
        if fUseColors:
            ii.pixel = self.cmap.lookup_with_dca(solid, colors)
        else:
            ii.pixel = self.cmap.lookup_with_transfer(dist, solid)
        ii.fate = fate
        ii.index = dist
        ii.iter = iter_
    def recolor(self, ii):
        dist = ii.index
        fate = ii.fate
        solid = 0
        inside = 0
        if fate & FATE_DIRECT:
            return
        if fate & FATE_SOLID:
            solid = 1
        if fate & FATE_INSIDE:
            inside = 1
        ii.pixel = self.cmap.lookup_with_transfer(dist, solid)

class im_info:
    def __init__(self, im):
        self.im = im
    def init_fate(self, x, y):
        self.index = 0.0
        self.iter = 0
        self.fate = self.im.getFate(x,y,0)
    def init(self, x, y):
        self.index = self.im.getIndex(x,y,0)
        self.iter = self.im.getIter(x,y)
        self.fate = self.im.getFate(x,y,0)
        self.pixel = self.im.get(x,y)
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

class fractFunc:
    def __init__(self, params, maxiter, worker, im):
        self.params = params
        self.maxiter = maxiter
        self.worker = worker
        self.im = im

        center = np.asarray([params[XCENTER], params[YCENTER], params[ZCENTER], params[WCENTER]])

        rot = rotated_matrix(params)

        rot = rot / im.totalXres()

        self.deltax = rot[VX].getA1()
        self.deltay = -rot[VY].getA1()

        delta_aa_x = self.deltax / 2.0
        delta_aa_y = self.deltay / 2.0

        topleft = center - self.deltax * im.totalXres() / 2.0 - self.deltay * im.totalYres() / 2.0

        topleft += im.Xoffset() * self.deltax;
        topleft += im.Yoffset() * self.deltay;

        topleft += delta_aa_x + delta_aa_y;

        self.topleft = topleft

    def draw(self):
        rsize = 16; drawsize = 16
        w = self.im.Xres(); h = self.im.Yres()
        y = 0
        while y < h - rsize:
            self.worker.qbox_row(w,y,rsize,drawsize)
            y += rsize
        while y < h:
            self.worker.row(0,y,w)
            y += 1
        y = 0
        while y < h - rsize:
            self.worker.box_row(w,y,rsize)
            y += rsize

(RGB, HSV_CCW, HSV_CW) = (0, 1, 2)
(BLEND_LINEAR,BLEND_CURVED,BLEND_SINE,BLEND_SPHERE_INCREASING,BLEND_SPHERE_DECREASING) = (0,1,2,3,4)

class gradient_item_t:
    def __init__(self):
        self.left = 0
        self.right = 0
        self.bmode = BLEND_LINEAR
        self.cmode = RGB

class ColorMap:
    def __init__(self, ncolors):
        self.ncolors = ncolors
        items = []
        for i in range(ncolors):
            the = gradient_item_t()
            items.append(the)
        self.items = items
    def lookup_with_dca(self, solid, colors):
        black = [0,0,0,255]
        if solid:
            return black
        r = 255.0 * colors[0]
        g = 255.0 * colors[1]
        b = 255.0 * colors[2]
        a = 255.0 * colors[3]
        return (r,g,b,a)
    def lookup_with_transfer(self, index, solid):
        black = [0,0,0,255]
        if solid:
            return black
        return self.lookup(index)
    def lookup(self, input_index):
        index = 1.0 if input_index == 1.0 else input_index - int(input_index)
        i = grad_find(index, self.items, self.ncolors)
        seg = self.items[i]
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
            assert False
        lc = seg.left_color
        rc = seg.right_color
        if seg.cmode == RGB:
            r = 255.0 * (lc[0] + (rc[0] - lc[0]) * factor) # how to convert to unsigned char
            g = 255.0 * (lc[1] + (rc[1] - lc[1]) * factor)
            b = 255.0 * (lc[2] + (rc[2] - lc[2]) * factor)
            a = 255.0 * (lc[3] + (rc[3] - lc[3]) * factor)
            return (r,g,b,a)
        elif seg.cmode in (HSV_CCW, HSV_CW):
            pass
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
            return (r*255.0, g*255.0, b*255.0, a)
        else:
            assert False
    def set(self, i, left, right, mid, left_col, right_col, bmode, cmode):
        self.items[i].left = left
        self.items[i].right = right
        self.items[i].mid = mid
        self.items[i].left_color = left_col
        self.items[i].right_color = right_col
        self.items[i].bmode = bmode
        self.items[i].cmode = cmode

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

def calc_4(params, maxiter, pfo, cmap, im):
    w = STFractWorker(pfo, cmap, im)
    ff = fractFunc(params, maxiter, w, im)
    w.ff = ff
    ff.draw()

if True:
    try:
        import fract4dcgmp as fract4dc
    except ImportError, err:
        import fract4dc

else:
    fract4dc = MyFract4dc()


