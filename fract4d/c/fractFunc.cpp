#include "fractFunc.h"
#include <stdio.h>
#include <stdlib.h>

#ifndef WIN32
#include <sys/time.h>
#else
struct timeval {
        long    tv_sec;         /* seconds */
        long    tv_usec;        /* and microseconds */
};
#include <sys/timeb.h>
int gettimeofday (struct timeval *t, void *foo)
{
        struct _timeb temp;
        _ftime(&temp);
        t->tv_sec = (long)temp.time;
        t->tv_usec = temp.millitm * 1000;
        return (0);
}
#endif

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

// The eye vector is the line between the center of the screen and the
// point where the user's eye is deemed to be. It's effectively the line
// perpendicular to the screen in the -Z direction, scaled by the "eye distance"

dvec4
test_eye_vector(double *params, double dist)
{
    dmat4 mat = rotated_matrix(params);
    return mat[VZ] * -dist;
}

double
gettimediff(struct timeval& startTime, struct timeval& endTime)
{
    long int diff_usec = endTime.tv_usec - startTime.tv_usec;
    if(diff_usec < 0)
    {
        endTime.tv_sec -= 1;
        diff_usec = 1000000 + diff_usec; 
    }
    return (double)(endTime.tv_sec - startTime.tv_sec) + (double)diff_usec/1000000.0;
}
 
fractFunc::fractFunc(
        d *params_,
        int maxiter_,
        IFractWorker *fw,
        IImage *im_, 
        IFractalSite *site_)
{
    site = site_;
    im = im_;
    ok = true;
    debug_flags = 0;
    render_type = RENDER_TWO_D;
    //printf("render type %d\n", render_type);
    worker = fw;
    params = params_;

    maxiter = maxiter_;
    // period_tolerance = 0.0;
    // warp_param = -1;

    set_progress_range(0.0,1.0);
    /*
    printf("(%d,%d,%d,%d,%d,%d)\n", 
           im->Xres(), im->Yres(), im->totalXres(), im->totalYres(),
           im->Xoffset(), im->Yoffset());
    */
    dvec4 center = dvec4(params[XCENTER],params[YCENTER], params[ZCENTER],params[WCENTER]);

    rot = rotated_matrix(params);

    eye_point = center + rot[VZ] * -10.0; // FIXME add eye distance parameter

    rot = rot/im->totalXres();
    // distance to jump for one pixel down or across
    deltax = rot[VX];
    // if yflip, draw Y axis down, otherwise up
    deltay = -rot[VY]; 

    // half that distance
    delta_aa_x = deltax / 2.0;    
    delta_aa_y = deltay / 2.0;

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
    
    worker->set_fractFunc(this);

    last_update_y = 0;
};


bool
fractFunc::update_image(int i)
{
    bool done = try_finished_cond();
    if(!done)
    {
        image_changed(0,last_update_y,im->Xres(),i);
        progress_changed((float)i/(float)im->Yres());
    }
    last_update_y = i;
    return done; 
}

// see if the image needs more (or less) iterations & tolerance to display properly

void fractFunc::reset_counts()
{
    worker->reset_counts();    
}

void fractFunc::reset_progress(float progress)
{
    worker->flush();
    image_changed(0,0,im->Xres(),im->Yres());
    progress_changed(progress);
}

// change everything with a fate of IN to UNKNOWN, because 
// image got deeper
void fractFunc::clear_in_fates()
{
    int w = im->Xres();
    int h = im->Yres();
    // FIXME can end up with some subpixels known and some unknown
    for(int y = 0; y < h; ++y)
    {
        for(int x = 0; x < w; ++x)
        {
            for(int n = 0; n < im->getNSubPixels(); ++n)
            {
                fate_t f = im->getFate(x,y,n);
                if(f & FATE_INSIDE)
                {
                    im->setFate(x,y,n, FATE_UNKNOWN);
                }
            }
        }
    }
}


void fractFunc::draw_all()
{
    status_changed(GF4D_FRACTAL_CALCULATING);
    
#if !defined(NO_CALC)
    // NO_CALC is used to stub out the actual fractal stuff so we can
    // profile & optimize the rest of the code without it confusing matters

    float minp = 0.0, maxp= 0.3; 
    draw(16,16,minp,maxp);    

    minp = 0.5; maxp = 0.9; // (eaa == AA_NONE ? 0.9 : 0.5);
    {
        set_progress_range(0.0,1.0);
        progress_changed(1.0);
    }

#endif

    progress_changed(0.0);
    status_changed(GF4D_FRACTAL_DONE);
}

void 
fractFunc::draw(
    int rsize, int drawsize, float min_progress, float max_progress)
{
    if(debug_flags & DEBUG_QUICK_TRACE)
    {
        printf("drawing: %d\n", render_type);
    }
    reset_counts();

    // init RNG based on time before generating image
    time_t now;
    time(&now);
    srand((unsigned int)now);

    int y;
    int w = im->Xres();
    int h = im->Yres();

    /* reset progress indicator & clear screen */
    last_update_y = 0;
    reset_progress(min_progress);

    float mid_progress = (max_progress + min_progress)/2.0;
    set_progress_range(min_progress, mid_progress);

    // first pass - big blocks and edges
    for (y = 0 ; y < h - rsize ; y += rsize) 
    {
        worker->qbox_row (w, y, rsize, drawsize);
        if(update_image(y)) 
        {
            goto done;
        }
    }
 
    // remaining lines
    for ( ; y < h ; y++)
    {
        worker->row(0,y,w);
        if(update_image(y)) 
        {
            goto done;
        }
    }

    last_update_y = 0;
    reset_progress(0.0);
    set_progress_range(mid_progress, max_progress);

    // fill in gaps in the rsize-blocks
    for ( y = 0; y < h - rsize; y += rsize) 
    {
        worker->box_row(w,y,rsize);
        if(update_image(y))
        {
            goto done;
        }
    }

 done:
    /* refresh entire image & reset progress bar */
    reset_progress(1.0);
    stats_changed();
}

void calc_4(d *params,
    int maxiter,
    pf_obj *pfo, 
    ColorMap *cmap, 
    IImage *im, 
    IFractalSite *site)
{
    assert(NULL != im && NULL != site && 
           NULL != cmap && NULL != pfo && NULL != params);
    IFractWorker *worker = IFractWorker::create(pfo,cmap,im,site);

    if(worker && worker->ok())
    {
        fractFunc ff(
            params, 
            maxiter,
            worker,
            im,
            site);

        ff.draw_all();
    }
    delete worker;
}
