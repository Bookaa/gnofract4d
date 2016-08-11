#include "fractFunc.h"
#include "fractWorker.h"
#include <stdio.h>
#include <stdlib.h>


dmat4
rotated_matrix(double *params)
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
    this->ok = true;
    this->debug_flags = 0;
    this->render_type = RENDER_TWO_D;
    //printf("render type %d\n", render_type);
    this->worker = fw;

    this->maxiter = maxiter_;

    set_progress_range(0.0,1.0);
    /*
    printf("(%d,%d,%d,%d,%d,%d)\n", 
           im->Xres(), im->Yres(), im->totalXres(), im->totalYres(),
           im->Xoffset(), im->Yoffset());
    */
    dvec4 center = dvec4(params[XCENTER],params[YCENTER], params[ZCENTER],params[WCENTER]);

    this->rot = rotated_matrix(params);

    this->eye_point = center + rot[VZ] * -10.0; // FIXME add eye distance parameter

    this->rot = rot/im->totalXres();
    // distance to jump for one pixel down or across
    this->deltax = rot[VX];
    // if yflip, draw Y axis down, otherwise up
    this->deltay = -rot[VY]; 

    // half that distance
    this->delta_aa_x = deltax / 2.0;    
    this->delta_aa_y = deltay / 2.0;

    // topleft is now top left corner of top left pixel...
    topleft = center -
        deltax * im->totalXres() / 2.0 -
        deltay * im->totalYres() / 2.0;

    // offset to account for tiling, if any
    topleft += im->Xoffset() * deltax;
    topleft += im->Yoffset() * deltay;

    // .. then offset to center of pixel
    topleft += delta_aa_x + delta_aa_y;

    // antialias: offset to middle of top left quadrant of pixel
    aa_topleft = topleft - (delta_aa_y + delta_aa_x) / 2.0;
};


void fractFunc::draw_all()
{
    float minp = 0.0, maxp= 0.3; 
    draw(16,16,minp,maxp);    

    minp = 0.5; maxp = 0.9; // (eaa == AA_NONE ? 0.9 : 0.5);
    
    set_progress_range(0.0, 1.0);
}

void fractFunc::draw(int rsize, int drawsize, float min_progress, float max_progress)
{
    if(debug_flags & DEBUG_QUICK_TRACE)
    {
        printf("drawing: %d\n", render_type);
    }
    this->worker->reset_counts();

    // init RNG based on time before generating image
    int y;
    int w = im->Xres();
    int h = im->Yres();

    /* reset progress indicator & clear screen */
    reset_progress(min_progress);

    float mid_progress = (max_progress + min_progress)/2.0;
    set_progress_range(min_progress, mid_progress);

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

    reset_progress(0.0);
    set_progress_range(mid_progress, max_progress);

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) 
    {
        worker->box_row(w,y,rsize);
    }

    /* refresh entire image & reset progress bar */
    reset_progress(1.0);
}

void calc_4(d *params, int maxiter, pf_obj *pfo, ColorMap *cmap, IImage *im)
{
    assert(NULL != im && NULL != site && NULL != cmap && NULL != pfo && NULL != params);

    STFractWorker w = STFractWorker();
    bool ok = w.init(pfo,cmap,im);

    IFractWorker *worker = &w; // IFractWorker::create(pfo,cmap,im);

    if (ok)
    {
        fractFunc ff(params, maxiter, worker, im);

        worker->set_fractFunc(&ff);

        ff.draw_all();
    }
}
