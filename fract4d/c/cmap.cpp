/* a cmap is a mapping from double [0.0,1.0] (#index) -> color */

#include "cmap.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>

#include <new>

rgba_t black = {0,0,0,255};

#define EPSILON 1.0e-10

void
cmap_delete(ColorMap *cmap)
{
    assert(cmap->canary == 0xfeeefeee);
    delete cmap;
}

rgba_t
ColorMap::lookup_with_dca(int solid, double *colors) const
{
    rgba_t new_color;

    if(solid)
    {
        return black; //solids[inside];
    }

    e_transferType t = TRANSFER_LINEAR; // transfers[inside];
    switch(t)
    {
    case TRANSFER_NONE:
        return black; // solids[inside];
    case TRANSFER_LINEAR:
        new_color.r = (unsigned char)(255.0 * colors[0]);
        new_color.g = (unsigned char)(255.0 * colors[1]);
        new_color.b = (unsigned char)(255.0 * colors[2]);
        new_color.a = (unsigned char)(255.0 * colors[3]);
        return new_color;
    default:
        assert("bad transfer type" && 0);
        return black;
    }
}
 
rgba_t
ColorMap::lookup_with_transfer(double index, int solid) const
{
    if(solid)
    {
        return black; // solids[inside];
    }
    
    e_transferType t = TRANSFER_LINEAR; // transfers[inside];
    switch(t)
    {
    case TRANSFER_NONE:
        return black; // solids[inside];
    case TRANSFER_LINEAR:
        return lookup(index);
    default:
        assert("bad transfer type" && 0);
        return black;
    }
}

bool
GradientColorMap::init(int ncolors_)
{
    if(ncolors_ == 0)
    {
        return false;
    }

    ncolors = ncolors_; 

    items = new(std::nothrow) gradient_item_t[ncolors];
    if(!items)
    {
        return false;
    }

    for(int i = 0; i < ncolors; ++i)
    {
        gradient_item_t *p = &items[i];
        p->left = p->right = 0;
        p->bmode = BLEND_LINEAR;
        p->cmode = RGB;
    }
    return true;
}

void GradientColorMap::set(int i,
    double left, double right, double mid,
    double *left_col,
    double *right_col,
    e_blendType bmode, e_colorType cmode)
{
    items[i].left = left;
    items[i].right = right;
    items[i].mid = mid;
    for(int j = 0; j < 4 ; ++j)
    {
        items[i].left_color[j] = left_col[j];
        items[i].right_color[j] = right_col[j];
    }
    items[i].bmode = bmode;
    items[i].cmode = cmode;
}

static int grad_find(double index, gradient_item_t *items, int ncolors)
{
    for(int i = 0; i < ncolors; ++i)
    {
        if(index <= items[i].right)
        {
            return i;
        } 
    }
    assert(0 && "Didn't find an entry");
    return -1;
}

static double
calc_linear_factor (double middle, double pos)
{
  if (pos <= middle)
    {
      if (middle < EPSILON)
        return 0.0;
      else
        return 0.5 * pos / middle;
    }
  else
    {
      pos -= middle;
      middle = 1.0 - middle;

      if (middle < EPSILON)
        return 1.0;
      else
        return 0.5 + 0.5 * pos / middle;
    }
}

static double
calc_curved_factor (double middle,double pos)
{
  if (middle < EPSILON)
    middle = EPSILON;

  return pow (pos, log (0.5) / log (middle));
}

static double
calc_sine_factor (double middle, double pos)
{
    pos = calc_linear_factor (middle, pos);
    return (sin ((-M_PI / 2.0) + M_PI * pos) + 1.0) / 2.0;
}

static double
calc_sphere_increasing_factor (double middle,
                               double pos)
{
    pos = calc_linear_factor (middle, pos) - 1.0;
    return sqrt (1.0 - pos * pos); 
}

static double
calc_sphere_decreasing_factor (double middle,
                               double pos)
{
    pos = calc_linear_factor (middle, pos);
    return 1.0 - sqrt(1.0 - pos * pos);
}

#define MAX3(a,b,c) ((a) > (b) ? \
                       ((a) > (c) ? (a) : (c)) : \
                       ((b) > (c) ? (b) : (c)))

#define MIN3(a,b,c) ((a) < (b) ? \
                       ((a) < (c) ? (a) : (c)) : \
                       ((b) < (c) ? (b) : (c)))
  
static void rgb_to_hsv(double r, double g, double b, double *h, double *s, double *v)
{
    double min = MIN3( r, g, b );
    double max = MAX3( r, g, b );
    *v = max;                   

    double delta = max - min;

    *s = (max == 0.0) ? 0.0 : (delta/max);

    if(*s == 0.0)
    {
        // achromatic
        *h = 0; // strictly, undefined. we choose 0
        return;
    }
    
    if( r == max )
    {
        *h = ( g - b ) / delta;                // between yellow & magenta
    }
    else if( g == max )
    {
        *h = 2 + ( b - r ) / delta;        // between cyan & yellow
    }    
    else
    {
        *h = 4 + ( r - g ) / delta;        // between magenta & cyan
    }

    if( *h < 0 )
    {
        *h += 6.0;
    }
}

static void gimp_rgb_to_hsv(double r, double g, double b, double *h, double *s, double *v) 
{
    rgb_to_hsv(r,g,b,h,s,v);
    *h /= 6.0;
}
static void hsv_to_rgb(double h, double s, double v, double *r, double *g, double *b)
{
    /* 0 <= h < 6 */
    if(s == 0)
    {
        *r = *g = *b = v;
        return;
    }

    h = fmod(h,6.0);
    if(h < 0)
    {
        h += 6.0;
    }

    int i = int(h);
    double f = h - i; //Decimal bit of hue
    double p = v * (1 - s);
    double q = v * (1 - s * f);
    double t = v * (1 - s * (1 - f));
    
    switch(i)
    {
    case 0:
        *r = v; *g = t; *b = p;
        break;
    case 1:
        *r = q; *g = v; *b = p;
        break;
    case 2:
        *r = p; *g = v; *b = t;
        break;
    case 3:
        *r = p; *g = q; *b = v;
        break;
    case 4:
        *r = t; *g = p; *b = v;
        break;
    case 5:
        *r = v; *g = p; *b = q;
    }
}

static void gimp_hsv_to_rgb(double h, double s, double v, double *r, double *g, double *b)
{
    h *= 6.0; // h*360/60
    hsv_to_rgb(h,s,v,r,g,b);
}

rgba_t 
GradientColorMap::lookup(double input_index) const
{
    assert(canary == 0xfeeefeee);
    double index = input_index == 1.0 ? 1.0 : fmod(input_index,1.0);
    if(index < 0.0 || index > 1.0 || index != index)
    {
        // must be infinite or NaN
        return black;
    }
    int i = grad_find(index, items, ncolors); 
    assert(i >= 0 && i < ncolors);

    gradient_item_t *seg = &items[i];

    double seg_len = seg->right - seg->left;
    
    double middle;
    double pos;
    if (seg_len < EPSILON)
    {
        middle = 0.5;
        pos    = 0.5;
    }
    else
    {
        middle = (seg->mid - seg->left) / seg_len;
        pos    = (index - seg->left) / seg_len;
    }
    
    double factor;
    switch (seg->bmode)
    {
    case BLEND_LINEAR:
        factor = calc_linear_factor (middle, pos);
        break;
    
    case BLEND_CURVED:
        factor = calc_curved_factor (middle, pos);
        break;
      
    case BLEND_SINE:
        factor = calc_sine_factor (middle, pos);
        break;
    
    case BLEND_SPHERE_INCREASING:
        factor = calc_sphere_increasing_factor (middle, pos);
        break;
    
    case BLEND_SPHERE_DECREASING:
        factor = calc_sphere_decreasing_factor (middle, pos);
        break;
    
    default:
        assert(0 && "Unknown gradient type");
        return black;
    }

    /* Calculate color components */
    rgba_t result;
    double *lc = seg->left_color;
    double *rc = seg->right_color;
    switch (seg->cmode) {
    case RGB:
        result.r = (unsigned char)(255.0 * (lc[0] + (rc[0] - lc[0]) * factor));
        result.g = (unsigned char)(255.0 * (lc[1] + (rc[1] - lc[1]) * factor));
        result.b = (unsigned char)(255.0 * (lc[2] + (rc[2] - lc[2]) * factor));
        break;
    case HSV_CCW:
    case HSV_CW:
        double lh,ls,lv;
        double rh,rs,rv;

        gimp_rgb_to_hsv (lc[0], lc[1], lc[2], &lh, &ls, &lv);
        gimp_rgb_to_hsv (rc[0], rc[1], rc[2], &rh, &rs, &rv);

        if (seg->cmode == HSV_CCW && lh >= rh)
        {
            rh += 1.0;
        } 
        if (seg->cmode == HSV_CW && lh <= rh )
        { 
            lh += 1.0;
        }
                
        double h,s,v;
        h = lh + (rh - lh) * factor;
        s = ls + (rs - ls) * factor;
        v = lv + (rv - lv) * factor;
                
        if ( h > 1.0 ) { h -= 1.0; }
        //fprintf(stderr,"HSV  %f %f %f FACTOR %f POS %f\n", h,s,v,factor,pos);
                
        double r,g,b;
        gimp_hsv_to_rgb(h, s, v, &r, &g, &b);
        result.r = (unsigned char)(255.0 * r);
        result.g = (unsigned char)(255.0 * g);
        result.b = (unsigned char)(255.0 * b);
      
        break;
    default:
        assert(0 && "Unknown color type");
        result = black;
        break;
    }

    /* Calculate alpha */
    result.a = (unsigned char)(255.0 * (lc[3] + (rc[3] - lc[3]) * factor));
    return result;
}

