
#include "fract_stdlib.h"
#include "pf.h"
#include "cmap.h"
#include "pointFunc_public.h"
#include "fract_public.h"
#include "image_public.h"

void pointFunc::calc_pf(const double *params, int nIters, struct im_info * ii) const
{
    rgba_t *color = &ii->pixel;
    int *pnIters = &ii->iter;
    float *pIndex = &ii->index;
    fate_t *pFate = &ii->fate;

    double dist = 0.0; 
    int fate = 0;
    int solid = 0;
    int fUseColors = 0;
    double colors[4] = {0.0};

    m_pfo->vtbl->calc(m_pfo, params, nIters, 
        pnIters, &fate, &dist, &solid,
        &fUseColors, &colors[0]);

    if (fUseColors)
    {
        *color = m_cmap->lookup_with_dca(solid, colors);
    }
    else
    {
        *color = m_cmap->lookup_with_transfer(dist, solid);
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
    ii.pixel = m_cmap->lookup_with_transfer(dist, solid);
}




