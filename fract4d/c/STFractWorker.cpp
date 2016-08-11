#include "fractFunc.h"
#include "pointFunc_public.h"
#include "fractWorker.h"
#include <stdio.h>
#include <stdlib.h>


void
STFractWorker::row(int x, int y, int n)
{
    for(int i = 0; i < n; ++i)
    {
        pixel(x+i,y,1,1);
    }
}

void
STFractWorker::col(int x, int y, int n)
{
    for(int i = 0; i < n; ++i)
    {
        pixel(x,y+i,1,1);
    }
}

inline int 
STFractWorker::RGB2INT(int x, int y)
{
    rgba_t pixel = im->get(x,y);
    return Pixel2INT(pixel);
}

inline int
STFractWorker::Pixel2INT(rgba_t pixel)
{
    int ret = (pixel.r << 16) | (pixel.g << 8) | pixel.b;
    return ret;
}

inline bool STFractWorker::isTheSame(
    bool bFlat, int targetIter, int targetCol, int x, int y)
{
    if (!bFlat) return false;
    // does this point have the target # of iterations?
    if(im->getIter(x,y) != targetIter) return false;
    // does it have the same colour too?
    if(RGB2INT(x,y) != targetCol) return false;
    return true;
}

void
STFractWorker::compute_stats(const dvec4& pos, int iter, fate_t fate, int x, int y)
{
    /*stats.s[ITERATIONS] += iter;
    stats.s[PIXELS]++;
    stats.s[PIXELS_CALCULATED]++;
    if (fate & FATE_INSIDE)
    {
        stats.s[PIXELS_INSIDE]++;
        if (iter < ff->maxiter-1)
        {
            stats.s[PIXELS_PERIODIC]++;
        }
    }
    else
    {
        stats.s[PIXELS_OUTSIDE]++;
    }*/
}

void 
STFractWorker::pixel(int x, int y, int w, int h)
{
    pointFunc pf = pointFunc(m_pfo, m_cmap);

    rgba_t pixel;
    float index = 0.0;

    fate_t fate = im->getFate(x,y,0);

    if (fate == FATE_UNKNOWN)
    {
        int iter = 0;
        
        switch(ff->render_type)
        {
        case RENDER_TWO_D: 
        {
            // calculate coords of this point
            dvec4 pos = ff->topleft + x * ff->deltax + y * ff->deltay;

            pf.calc_pf(pos.n, ff->maxiter, x, y, &pixel, &iter, &index, &fate);

            compute_stats(pos,iter,fate,x,y);
        }
        break;
        case RENDER_LANDSCAPE:
            assert(0 && "not supported");
            break;

        case RENDER_THREE_D:
            assert(0 && "not supported");
            break;
        }

        assert(fate != FATE_UNKNOWN);
        im->setIter(x,y,iter);
        im->setFate(x,y,0,fate);
        im->setIndex(x,y,0,index);
    }
    else
    {
        pixel = pf.recolor(im->getIndex(x,y,0), fate, im->get(x,y));
    }
    rectangle(pixel,x,y,w,h);
}

void 
STFractWorker::box_row(int w, int y, int rsize)
{
    // we increment by rsize-1 because we want to reuse the vertical bars
    // between the boxes - each box overlaps by 1 pixel
    int x;
    for(x = 0; x < w - rsize ; x += rsize -1) {
        box(x,y,rsize);            
    }           
    // extra pixels at end of lines
    for(int y2 = y; y2 < y + rsize; ++y2)
    {
        row (x, y2, w-x);
    }
}

void
STFractWorker::qbox_row(int w, int y, int rsize, int drawsize)
{
    int x;
    // main large blocks 
    for (x = 0 ; x< w - rsize ; x += rsize -1) 
    {
        pixel ( x, y, drawsize, drawsize);
    }
    // extra pixels at end of lines
    for(int y2 = y; y2 < y + rsize; ++y2)
    {
        row (x, y2, w-x);
    }
}

bool 
STFractWorker::isNearlyFlat(int x, int y, int rsize)
{
    rgba_t colors[2];
    fate_t fate = im->getFate(x,y,0);

    const int MAXERROR=3;

    // can we predict the top edge close enough?
    colors[0] = im->get(x,y); // topleft
    colors[1] = im->get(x+rsize-1,y); //topright
    int x2;

    for (x2 = x+1; x2 < x+rsize-1; ++x2)
    {
        if (im->getFate(x2,y,0) != fate) return false;

        rgba_t predicted = predict_color(colors,(double)(x2-x)/rsize);
        int diff = diff_colors(predicted, im->get(x2,y));
        if (diff > MAXERROR)
        {
            return false;
        }
    }

    // how about the bottom edge?
    int y2 = y + rsize -1;
    colors[0] = im->get(x,y2); // botleft
    colors[1] = im->get(x+rsize-1,y2); // botright

    for (x2 = x+1; x2 < x+rsize-1; ++x2)
    {
        if (im->getFate(x2,y2,0) != fate) return false;

        rgba_t predicted = predict_color(colors,(double)(x2-x)/rsize);
        int diff = diff_colors(predicted, im->get(x2,y2));
        if (diff > MAXERROR)
        {
            return false;
        }
    }

    // how about the left side?
    colors[0] = im->get(x,y); 
    colors[1] = im->get(x,y+rsize-1); 

    for (y2 = y+1; y2 < y+rsize-1; ++y2)
    {
        if (im->getFate(x,y2,0) != fate) return false;

        rgba_t predicted = predict_color(colors,(double)(y2-y)/rsize);
        int diff = diff_colors(predicted, im->get(x,y2));
        if (diff > MAXERROR)
        {
            return false;
        }
    }

    // and finally the right
    x2 = x + rsize-1;
    colors[0] = im->get(x2,y); 
    colors[1] = im->get(x2,y+rsize-1); 

    for (y2 = y+1; y2 < y+rsize-1; ++y2)
    {
        if (im->getFate(x2,y2,0) != fate) return false;

        rgba_t predicted = predict_color(colors,(double)(y2-y)/rsize);
        int diff = diff_colors(predicted, im->get(x2,y2));
        if (diff > MAXERROR)
        {
            return false;
        }
    }

    return true;
}

// linearly interpolate over a rectangle
void
STFractWorker::interpolate_rectangle(int x, int y, int rsize)
{
    for (int y2 = y ; y2 < y+rsize-1; ++y2)
    {
        interpolate_row(x,y2,rsize);
    }
}

void
STFractWorker::interpolate_row(int x, int y, int rsize)
{
    fate_t fate = im->getFate(x,y,0);
    rgba_t colors[2];
    colors[0] = im->get(x,y); // left
    colors[1] = im->get(x+rsize-1,y); //right
    int iters[2];
    iters[0] = im->getIter(x,y);
    iters[1] = im->getIter(x+rsize-1,y);

    int indexes[2];
    indexes[0] = im->getIndex(x,y,0);
    indexes[1] = im->getIndex(x+rsize-1,y,0);
    
    for (int x2 =x ; x2 < x+rsize-1; ++x2)
    {
        double factor = (double)(x2-x)/rsize;
        rgba_t predicted_color = predict_color(colors, factor);
        int predicted_iter = predict_iter(iters, factor);
        float predicted_index = predict_index(indexes, factor);

        //check_guess(x2,y,predicted_color,fate,predicted_iter,predicted_index);
        im->put(x2,y,predicted_color);  
        im->setIter(x2,y,predicted_iter);
        im->setFate(x2,y,0,fate);
        im->setIndex(x2,y,0,predicted_index);
        //stats.s[PIXELS]++;
        //stats.s[PIXELS_SKIPPED]++;
    }
}

// linearly interpolate between colors to guess correct color
rgba_t
STFractWorker::predict_color(rgba_t colors[2], double factor)
{
    rgba_t result;
    result.r = (int)(colors[0].r * (1.0 - factor) + colors[1].r * factor);
    result.g = (int)(colors[0].g * (1.0 - factor) + colors[1].g * factor);
    result.b = (int)(colors[0].b * (1.0 - factor) + colors[1].b * factor);
    result.a = (int)(colors[0].a * (1.0 - factor) + colors[1].a * factor);
    return result;
}

int
STFractWorker::predict_iter(int iters[2], double factor)
{
    return (int)(iters[0] * (1.0 - factor) + iters[1] * factor);
}

float
STFractWorker::predict_index(int indexes[2], double factor)
{
    return (indexes[0] * (1.0 - factor) + indexes[1] * factor);
}


// sum squared differences between components of 2 colors
int
STFractWorker::diff_colors(rgba_t a, rgba_t b)
{
    int dr = a.r - b.r;
    int dg = a.g - b.g;
    int db = a.b - b.b;
    int da = a.a - b.a;

    return dr*dr + dg*dg + db*db + da*da;
}

void 
STFractWorker::box(int x, int y, int rsize)
{
    // calculate edges of box to see if they're all the same colour
    // if they are, we assume that the box is a solid colour and
    // don't calculate the interior points
    bool bFlat = true;
    int iter = im->getIter(x,y);
    int pcol = RGB2INT(x,y);
    
    // calculate top and bottom of box & check for flatness
    for(int x2 = x; x2 < x + rsize; ++x2)
    {
        pixel(x2,y,1,1);
        bFlat = isTheSame(bFlat,iter,pcol,x2,y);
        pixel(x2,y+rsize-1,1,1);        
        bFlat = isTheSame(bFlat,iter,pcol,x2,y+rsize-1);
    }
    // calc left and right of box & check for flatness
    for(int y2 = y; y2 < y + rsize; ++y2)
    {
        pixel(x,y2,1,1);
        bFlat = isTheSame(bFlat, iter, pcol, x, y2);
        pixel(x+rsize-1,y2,1,1);
        bFlat = isTheSame(bFlat,iter,pcol,x+rsize-1,y2);
    }
    
    if(bFlat)
    {
        // just draw a solid rectangle
        rgba_t pixel = im->get(x,y);
        fate_t fate = im->getFate(x,y,0);
        float index = im->getIndex(x,y,0);
        rectangle_with_iter(pixel,fate,iter,index,x+1,y+1,rsize-2,rsize-2);
    }
    else
    {
        bool nearlyFlat = false && isNearlyFlat(x,y,rsize);
        if (nearlyFlat)
        {
            //printf("nf: %d %d %d\n", x, y, rsize);
            interpolate_rectangle(x,y,rsize);
        }
        else
        {
            //printf("bumpy: %d %d %d\n", x, y, rsize);

            if(rsize > 4)
            {       
                // divide into 4 sub-boxes and check those for flatness
                int half_size = rsize/2;
                box(x,y,half_size);
                box(x+half_size,y,half_size);
                box(x,y+half_size, half_size);
                box(x+half_size,y+half_size, half_size);
            }
            else
            {
                // we do need to calculate the interior 
                // points individually
                for(int y2 = y + 1 ; y2 < y + rsize -1; ++y2)
                {
                    row(x+1,y2,rsize-2);
                }
            }
        }
    }           
}

inline void
STFractWorker::rectangle(
    rgba_t pixel, int x, int y, int w, int h, bool force)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) 
        {
            im->put(j,i,pixel);
        }
    }
}

inline void
STFractWorker::rectangle_with_iter(
    rgba_t pixel, fate_t fate, int iter, float index, 
    int x, int y, int w, int h)
{
    for(int i = y ; i < y+h; i++)
    {
        for(int j = x; j < x+w; j++) 
        {
            im->put(j,i,pixel);
            im->setIter(j,i,iter);
            im->setFate(j,i,0,fate);
            im->setIndex(j,i,0,index);
            //stats.s[PIXELS]++;
            //stats.s[PIXELS_SKIPPED]++;
        }
    }
}

