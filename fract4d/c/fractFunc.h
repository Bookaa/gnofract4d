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

    void draw();

    friend class STFractWorker;

    dmat4 rot; // scaled rotation matrix
    dvec4 deltax, deltay; // step from 1 pixel to the next in x,y directions
    // dvec4 delta_aa_x, delta_aa_y; // offset between subpixels
    dvec4 topleft; // top left corner of screen

private:

    int maxiter;
    render_type_t render_type;

    IImage *im;    
    IFractWorker *worker;
};



#endif /* _FRACTFUNC_H_ */
