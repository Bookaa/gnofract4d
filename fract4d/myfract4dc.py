
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
        FATE_UNKNOWN = 255
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

def cmap_from_pyobject(segs):
    pass

class Empty:
    pass
class MyFract4dc:
    IMAGE_WIDTH = 0
    IMAGE_HEIGHT = 1
    IMAGE_TOTAL_WIDTH = 2
    IMAGE_TOTAL_HEIGHT = 3
    IMAGE_XOFFSET = 4
    IMAGE_YOFFSET = 5

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

        mycalc.init(the, 0)

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

        assert False
        # fract4dc.calc(pfo=pfunc, xoff=xoff, yoff=yoff, xres=xres, yres=yres)
    def image_save_all(self, _img, fp):
        FILE_TYPE_PNG = 1
        iw = ImageWriter(FILE_TYPE_PNG, fp, _img)
        iw.save_header()
        iw.save_title()
        iw.save_footer()
if True:
    try:
        import fract4dcgmp as fract4dc
    except ImportError, err:
        import fract4dc

else:
    fract4dc = MyFract4dc()