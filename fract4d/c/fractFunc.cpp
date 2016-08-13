#include "fractFunc.h"
#include "fractWorker.h"
#include <stdio.h>
#include <stdlib.h>


static dmat4 rotated_matrix(double *params)
{
    d one = d(1.0);
    d zero = d(0.0);
    dmat4 id = identity3D<d>(params[MAGNITUDE],zero);

    return id * 
        rotXY<d>(params[XYANGLE],one,zero) *
        rotXZ<d>(params[XZANGLE],one,zero) * 
        rotXW<d>(params[XWANGLE],one,zero) *
        rotYZ<d>(params[YZANGLE],one,zero) *
        rotYW<d>(params[YWANGLE],one,zero) *
        rotZW<d>(params[ZWANGLE],one,zero);
}

fractFunc::fractFunc(d *params, int maxiter_, IFractWorker *fw, IImage *im_)
{
    this->im = im_;
    this->render_type = RENDER_TWO_D;
    this->worker = fw;

    this->maxiter = maxiter_;

    dvec4 center = dvec4(params[XCENTER],params[YCENTER], params[ZCENTER],params[WCENTER]);

    dmat4 rot = rotated_matrix(params);

    rot = rot/im->totalXres();
    // distance to jump for one pixel down or across
    this->deltax = rot[VX];
    // if yflip, draw Y axis down, otherwise up
    this->deltay = -rot[VY]; 

    // half that distance
    dvec4 delta_aa_x = deltax / 2.0;    
    dvec4 delta_aa_y = deltay / 2.0;

    // topleft is now top left corner of top left pixel...
    topleft = center -
        deltax * im->totalXres() / 2.0 -
        deltay * im->totalYres() / 2.0;

    // offset to account for tiling, if any
    topleft += im->Xoffset() * deltax;
    topleft += im->Yoffset() * deltay;

    // .. then offset to center of pixel
    topleft += delta_aa_x + delta_aa_y;
};


void fractFunc::draw()
{
    int rsize = 16;
    int drawsize = 16;

    // init RNG based on time before generating image
    int y;
    int w = im->Xres();
    int h = im->Yres();

    // first pass - big blocks and edges
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        worker->qbox_row (w, y, rsize, drawsize);
    }
 
    // remaining lines
    for ( ; y < h ; y++)
    {
        worker->row(0,y,w);
    }

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) 
    {
        worker->box_row(w,y,rsize);
    }
}

void calc_4(d *params, int maxiter, pf_obj *pfo, ColorMap *cmap, IImage *im)
{
    assert(NULL != im && NULL != site && NULL != cmap && NULL != pfo && NULL != params);

    STFractWorker w = STFractWorker(pfo,cmap,im);

    IFractWorker *worker = &w; // IFractWorker::create(pfo,cmap,im);

    fractFunc ff(params, maxiter, worker, im);

    w.set_fractFunc(&ff);

    ff.draw();
}
