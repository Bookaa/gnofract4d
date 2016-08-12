#ifndef FRACT_WORKER_PUBLIC_H_
#define FRACT_WORKER_PUBLIC_H_

class IFractWorker {
public:

    // calculate a row of pixels
    virtual void row(int x, int y, int n) =0;

    // calculate an rsize-by-rsize box of pixels
    virtual void box(int x, int y, int rsize) =0;

    // calculate a row of boxes
    virtual void box_row(int w, int y, int rsize) =0;

    // calculate a row of boxes, quickly
    virtual void qbox_row(int w, int y, int rsize, int drawsize) =0;

    // calculate a single pixel
    virtual void pixel(int x, int y, int w, int h) =0;
};


#endif /* FRACT_WORKER_PUBLIC_H_ */
