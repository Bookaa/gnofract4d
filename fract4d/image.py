# A type representing an image - this wraps the underlying C++ image type
# exposed via fract4dmodule and provides some higher-level options around it

import os

try:
    import fract4dcgmp as fract4dc
except ImportError, err:
    import fract4dc

file_types = {
    ".jpg" : fract4dc.FILE_TYPE_JPG,
    ".jpeg" : fract4dc.FILE_TYPE_JPG,
    ".png" : fract4dc.FILE_TYPE_PNG,
    ".tga" :fract4dc.FILE_TYPE_TGA
    }

def file_matches():
    return [ "*" + x for x in file_types.keys()]

class T:
    FATE_SIZE = 4
    COL_SIZE = 3
    SOLID = 128
    OUT=0
    IN=32 | SOLID # in pixels have solid bit set
    UNKNOWN=255
    BLACK=[0,0,0]
    WHITE=[255,255,255]
    def __init__(self,xsize,ysize,txsize=-1,tysize=-1):
        self._img = fract4dc.image_create(xsize,ysize,txsize, tysize)
        self.fate_buf = fract4dc.image_fate_buffer(self._img,0,0)
        self.image_buf = fract4dc.image_buffer(self._img,0,0)

    def get_xsize(self):
        return self.get_dim(fract4dc.IMAGE_WIDTH)

    def get_ysize(self):
        return self.get_dim(fract4dc.IMAGE_HEIGHT)

    def get_total_xsize(self):
        return self.get_dim(fract4dc.IMAGE_TOTAL_WIDTH)

    def get_total_ysize(self):
        return self.get_dim(fract4dc.IMAGE_TOTAL_HEIGHT)

    def get_xoffset(self):
        return self.get_dim(fract4dc.IMAGE_XOFFSET)

    def get_yoffset(self):
        return self.get_dim(fract4dc.IMAGE_YOFFSET)
    
    def get_dim(self,dim):
        return fract4dc.image_dims(self._img)[dim]

    xsize = property(get_xsize)
    ysize = property(get_ysize)
    total_xsize = property(get_total_xsize)
    total_ysize = property(get_total_ysize)
    xoffset = property(get_xoffset)
    yoffset = property(get_yoffset)

    def get_suggest_string(self):
        k = file_types.keys()
        k.sort()
        available_types = ", ".join(k).upper()
        suggest_string = "Please use one of: " + available_types
        return suggest_string

    def lookup(self,x,y):
        return fract4dc.image_lookup(self._img,x,y)
    

    def file_type(self,name):
        ext = os.path.splitext(name)[1]
        if ext == "":
            raise ValueError(
                "No file extension in '%s'. Can't determine file format. %s" %\
                (name, self.get_suggest_string()))
        
        type = file_types.get(ext.lower(), None)
        if type == None:
            raise ValueError(
                "Unsupported file format '%s'. %s" % \
                (ext, self.get_suggest_string()))
        return type
    
    def save(self,name):
        # start_save :
        ft = self.file_type(name)
        try:
            fp = open(name, "wb")
        except IOError, err:
            raise IOError("Unable to save image to '%s' : %s" % (name,err.strerror))

        if True:
            fract4dc.image_save_all(self._img, fp)
        else:
            writer = fract4dc.image_writer_create(self._img, fp, ft)
            fract4dc.image_save_header(writer)

            # save_tile :
            if writer:
                fract4dc.image_save_tile(writer)

            # finish_save :
            fract4dc.image_save_footer(writer)
        fp.close()

    def get_tile_list(self):
        x = 0
        y = 0
        base_xres = self.xsize
        base_yres = self.ysize
        tiles = []
        while y < self.total_ysize:
            while x < self.total_xsize:
                w = min(base_xres, self.total_xsize - x)
                h = min(base_yres, self.total_ysize - y)
                tiles.append((x,y,w,h))
                x += base_xres
            y += base_yres
            x = 0
        return tiles


