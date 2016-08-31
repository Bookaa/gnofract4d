# A type representing an image - this wraps the underlying C++ image type
# exposed via fract4dmodule and provides some higher-level options around it

import myfract4dc
#fract4dc = myfract4dc.fract4dc


class T:
    def __init__(self,xsize,ysize,txsize=-1,tysize=-1):
        self._img = myfract4dc.image_create(xsize, ysize, txsize, tysize)

    def save(self,name):
        from skimage.io import imsave # scikit-image (0.12.3)
        buf1 = self._img.buffer.reshape((self._img.Yres(), self._img.Xres(), 3))
        imsave(name, buf1)

    def old_save(self,name):
        try:
            fp = open(name, "wb")
        except IOError, err:
            raise IOError("Unable to save image to '%s' : %s" % (name,err.strerror))

        myfract4dc.image_save_all(self._img, fp)

        fp.close()

    def get_tile_list(self):
        dims = myfract4dc.image_dims(self._img)
        xsize = dims[myfract4dc.IMAGE_WIDTH]
        ysize = dims[myfract4dc.IMAGE_HEIGHT]
        total_xsize = dims[myfract4dc.IMAGE_TOTAL_WIDTH]
        total_ysize = dims[myfract4dc.IMAGE_TOTAL_HEIGHT]
        x = 0
        y = 0
        base_xres = xsize
        base_yres = ysize
        tiles = []
        while y < total_ysize:
            while x < total_xsize:
                w = min(base_xres, total_xsize - x)
                h = min(base_yres, total_ysize - y)
                tiles.append((x,y,w,h))
                x += base_xres
            y += base_yres
            x = 0
        return tiles


