/* The RGB buffer which the fractal-drawing process writes into. */

#ifndef _IMAGE_H_
#define _IMAGE_H_

#include "image_public.h"

#include <cassert>

class image : public IImage
{
    int m_Xres;
    int m_Yres;

    int m_totalXres, m_totalYres;
    int m_xoffset, m_yoffset;

    /* the RGB colours of the image */
    char *buffer;

    /* the iteration count for each pixel */
    int *iter_buf;

    /* the value of #index for each pixel */
    float *index_buf;

    /* the fate of each pixel */
    fate_t *fate_buf;

    void delete_buffers();
    bool alloc_buffers();

public:
    static const int N_SUBPIXELS;

    image();
    image(const image& im);
    ~image();

    bool ok() { return buffer != NULL; };

    inline int Xres() const { return m_Xres; };
    inline int Yres() const { return m_Yres; };

    inline int totalXres() const { return m_totalXres; };
    inline int totalYres() const { return m_totalYres; };

    inline int Xoffset() const  { return m_xoffset; };
    inline int Yoffset() const  { return m_yoffset; };

    inline char* getBuffer() const
    {
        assert(buffer != NULL);
        return buffer;
    };

    // utilities

    int bytes() const;

    // accessors
    void put(int x, int y, rgba_t pixel);
    rgba_t get(int x, int y) const;

    int getIter(int x, int y) const
    {
        return iter_buf[x + y * m_Xres];
    };

    void setIter(int x, int y, int iter)
    {
        iter_buf[x + y * m_Xres] = iter;
    };

    bool hasFate() const
    {
        return fate_buf != NULL;
    }

    fate_t getFate(int x, int y, int subpixel) const;
    void setFate(int x, int y, int subpixel, fate_t fate);

    float getIndex(int x, int y, int subpixel) const;
    void setIndex(int x, int y, int subpixel, float index);

    int index_of_subpixel(int x, int y, int subpixel) const
    {
        assert(subpixel >= 0 && subpixel < N_SUBPIXELS);
        assert(x >= 0 && x < m_Xres);
        assert(y >= 0 && y < m_Yres);

        return (y * m_Xres + x) * N_SUBPIXELS + subpixel;
    };

    bool set_resolution(int x, int y, int totalx, int totaly);
    bool set_offset(int x, int y);

    void clear();
};


#endif /* _IMAGE_H_ */
