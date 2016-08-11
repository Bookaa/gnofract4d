#ifndef _FRACTFUNC_H_
#define _FRACTFUNC_H_

#include <cassert>

#include "image_public.h"
#include "pointFunc_public.h"
#include "fractWorker_public.h"
#include "vectors.h"
#include "fract_public.h"

/* this contains stuff which is useful for drawing the fractal,
   but can be recalculated at will, so isn't part of the fractal's
   persistent state. We create a new one each time we start drawing. This one
   parcels up the work which is actually performed by the fractThreadFuncs
 */


class fractFunc {
 public:
    fractFunc(d *params,
        int maxiter,
        IFractWorker *fw,
        IImage *_im);
    // ~fractFunc();

    void draw();

    friend class STFractWorker;

    // used for calculating (x,y,z,w) pixel coords
    dmat4 rot; // scaled rotation matrix
    dvec4 deltax, deltay; // step from 1 pixel to the next in x,y directions
    dvec4 delta_aa_x, delta_aa_y; // offset between subpixels
    dvec4 topleft; // top left corner of screen
    //dvec4 aa_topleft; // topleft - offset to 1st subpixel to draw
    //dvec4 eye_point; // where user's eye is (for 3d mode)

 private:

    int maxiter;
    render_type_t render_type;

    IImage *im;    
    IFractWorker *worker;
};

void calc_4(
    d *params,
    int maxiter,
    pf_obj *pfo, 
    ColorMap *cmap, 
    IImage *im);


#endif /* _FRACTFUNC_H_ */
