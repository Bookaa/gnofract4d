
#ifndef FRACT_WORKER_H_
#define FRACT_WORKER_H_

#include "fractWorker_public.h"
#include "pointFunc_public.h"

class STFractWorker : public IFractWorker {
    fractFunc *ff;
    pf_obj *m_pfo;
    ColorMap *m_cmap;

    IImage *im;

public:

    STFractWorker(pf_obj *pfo, ColorMap *cmap, IImage *im_)
    {
        this->ff = NULL;
        this->im = im_;

        this->m_pfo = pfo;
        this->m_cmap = cmap;
    }

    void set_fractFunc(fractFunc *ff) { this->ff = ff; }

    // calculate a row of pixels
    void row(int x, int y, int n);

    // calculate a column of pixels
    void nouse_col(int x, int y, int n);

    // calculate an rsize-by-rsize box of pixels
    void box(int x, int y, int rsize);

    // calculate a row of boxes
    void box_row(int w, int y, int rsize);

    // calculate a row of boxes, quickly
    void qbox_row(int w, int y, int rsize, int drawsize);

    // calculate a single pixel
    void pixel(int x, int y, int h, int w);

private:
    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);

    // linearly interpolate between colors to guess correct color
    rgba_t predict_color(rgba_t colors[2], double factor);
    int predict_iter(int iters[2], double factor);
    float predict_index(int indexes[2], double factor);

    // sum squared differences between components of 2 colors
    int diff_colors(rgba_t a, rgba_t b);

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int x, int y);

    void interpolate_row(int x, int y, int rsize);
};

#endif /* FRACT_WORKER_H_ */
