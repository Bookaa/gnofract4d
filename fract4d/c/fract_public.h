#ifndef _FRACT_PUBLIC_H_
#define _FRACT_PUBLIC_H_

#include <pthread.h>

// current state of calculation
typedef enum {
    GF4D_FRACTAL_DONE,
    GF4D_FRACTAL_CALCULATING,
    GF4D_FRACTAL_DEEPENING,
    GF4D_FRACTAL_ANTIALIASING,
    GF4D_FRACTAL_PAUSED,
    GF4D_FRACTAL_TIGHTENING
} calc_state_t;

// kind of antialiasing to do
typedef enum {
    AA_NONE = 0,
    AA_FAST,
    AA_BEST,
    AA_DEFAULT /* used only for effective_aa - means use aa from fractal */
} e_antialias;

// basic parameters defining position and rotation in R4
typedef enum {
    XCENTER,
    YCENTER,
    ZCENTER,
    WCENTER,
    MAGNITUDE,
    XYANGLE,
    XZANGLE,
    XWANGLE,
    YZANGLE,
    YWANGLE,
    ZWANGLE,
} param_t;

// number of elements in enum above
#define N_PARAMS 11

// kind of image to draw
typedef enum {
    RENDER_TWO_D, // standard mandelbrot view
    RENDER_LANDSCAPE, // heightfield
    RENDER_THREE_D // ray-traced 3D object
} render_type_t;

// how to draw the image
typedef enum {
    DRAW_GUESSING, // several passes, starting with large boxes 
    DRAW_TO_DISK   // complete all passes on one box_row before continuing
} draw_type_t;

// colorFunc indices
#define OUTER 0
#define INNER 1

//class colorizer;
class IImage;
typedef struct s_pixel_stat pixel_stat_t;

#include "pointFunc_public.h"

// a type which must be implemented by the user of 
// libfract4d. We use this to inform them of the progress
// of an ongoing calculation

// WARNING: if nThreads > 1, these can be called back on a different
// thread, possibly several different threads at the same time. It is
// the callee's responsibility to handle mutexing.

// member functions are do-nothing rather than abstract in case you
// don't want to do anything with them
struct calc_args;



#endif /* _FRACT_PUBLIC_H_ */
