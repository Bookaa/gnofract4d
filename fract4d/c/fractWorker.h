
#ifndef FRACT_WORKER_H_
#define FRACT_WORKER_H_

#include "fractWorker_public.h"
#include "pointFunc_public.h"

/* enum for jobs */
typedef enum {
    JOB_NONE,
    JOB_BOX,
    JOB_BOX_ROW,
    JOB_ROW,
    JOB_ROW_AA,
    JOB_QBOX_ROW
} job_type_t;

/* one unit of work */
typedef struct {
    job_type_t job;
    int x, y, param, param2;
} job_info_t;

/* per-worker-thread fractal info */
class STFractWorker : public IFractWorker {
 public:
    /* pointers to data also held in fractFunc */
    IImage *im;    

    /* not a ctor because we always create a whole array then init them */
    bool init(pf_obj *pfo, ColorMap *cmap, IImage *im);

    ~STFractWorker() {
        delete pf;
    }

    STFractWorker() {
        stats.reset();
    }

    void set_fractFunc(fractFunc *ff) { this->ff = ff; }

    // calculate a row of pixels
    void row(int x, int y, int n);

    // calculate a column of pixels
    void col(int x, int y, int n);

    // calculate an rsize-by-rsize box of pixels
    void box(int x, int y, int rsize);

    // does the point at (x,y) have the same colour & iteration count
    // as the target?
    inline bool isTheSame(bool bFlat, int targetIter, int targetCol, int x, int y);

    // is the square with its top-left corner at (x,y) close-enough to flat
    // that we could interpolate & get a decent-looking image?
    bool isNearlyFlat(int x, int y, int rsize);

    // linearly interpolate between colors to guess correct color
    rgba_t predict_color(rgba_t colors[2], double factor);
    int predict_iter(int iters[2], double factor);
    float predict_index(int indexes[2], double factor);

    // sum squared differences between components of 2 colors
    int diff_colors(rgba_t a, rgba_t b);

    // make an int corresponding to an RGB triple
    inline int RGB2INT(int x, int y);
    inline int Pixel2INT(rgba_t pixel);

    // calculate a row of boxes
    void box_row(int w, int y, int rsize);

    // calculate a row of boxes, quickly
    void qbox_row(int w, int y, int rsize, int drawsize);

    // calculate a single pixel
    void pixel(int x, int y, int h, int w);

    // draw a rectangle of this colour
    void rectangle(rgba_t pixel, 
		   int x, int y, int w, int h, 
		   bool force=false);

    void rectangle_with_iter(rgba_t pixel, fate_t fate, 
			     int iter, float index,
			     int x, int y, int w, int h);

    void interpolate_rectangle(int x, int y, int rsize);
    void interpolate_row(int x, int y, int rsize);

    bool ok() { return m_ok; }
 
 private:

    void compute_stats(const dvec4& pos, int iter, fate_t fate, int x, int y);

    fractFunc *ff;

    // function object which calculates the colors of points 
    // this is per-thread-func so it doesn't have to be re-entrant
    // and can have member vars
    pointFunc *pf; 

    pixel_stat_t stats;

    bool m_ok;
};

//#include "threadpool.h"


#endif /* FRACT_WORKER_H_ */
