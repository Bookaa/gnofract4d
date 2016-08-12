
#include "fract_stdlib.h"
#include "pf.h"
#include "cmap.h"
#include "pointFunc_public.h"
#include "fract_public.h"
#include "image_public.h"

void pointFunc::calc_pf(
    // in params
    const double *params, int nIters, 
    // only used for debugging
    int x, int y,
    // out params
    rgba_t *color, int *pnIters, float *pIndex, fate_t *pFate) const
{
    //int min_period_iters = nIters;
    //double period_tolerance = 0.0;
    //int warp_param = -1;
    //int aa = 0;
    double dist = 0.0; 
    int fate = 0;
    int solid = 0;
    int fUseColors = 0;
    double colors[4] = {0.0};

    // frequently here printf("call calc in pointFunc.cpp\n");
    m_pfo->vtbl->calc(
        m_pfo, params,
        nIters, //warp_param,
        //min_period_iters, period_tolerance,
        x, y, //aa,
        pnIters, &fate, &dist, &solid,
        &fUseColors, &colors[0]);

    int inside = 0;
    if (fate & FATE_INSIDE)
    {
        *pnIters = -1;
        inside = 1;
    }

    if (fUseColors)
    {
        *color = m_cmap->lookup_with_dca(solid, inside, colors);
        fate |= FATE_DIRECT;
    }
    else
    {
        *color = m_cmap->lookup_with_transfer(dist,solid, inside);
    }

    if (solid)
    {
        fate |= FATE_SOLID;
    }

    *pFate = (fate_t) fate;
    *pIndex = (float) dist;
}

void pointFunc::recolor(struct im_info& ii) const
{
    double dist = ii.index;
    fate_t fate = ii.fate;
    //rgba_t current = ii.pixel;

    int solid = 0;
    int inside = 0;
    if (fate & FATE_DIRECT)
    {
        return; // current;
    }
    if (fate & FATE_SOLID)
    {
        solid = 1;
    }
    if (fate & FATE_INSIDE)
    {
        inside = 1;
    }
    ii.pixel = m_cmap->lookup_with_transfer(dist,solid, inside);
}




