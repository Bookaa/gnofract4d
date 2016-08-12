#ifndef _POINTFUNC_PUBLIC_H_
#define _POINTFUNC_PUBLIC_H_

#include "pf.h"
#include "cmap.h"
#include "fate.h"

/* interface for function object which computes and/or colors a single point */
class pointFunc {
private:
    pf_obj *m_pfo;
    ColorMap *m_cmap;
public:
    pointFunc(pf_obj *pfo, ColorMap *cmap) :	m_pfo(pfo), m_cmap(cmap)
	{
	}
 public:
    void calc_pf(
        const double *params, int nIters, // in params. params points to [x,y,cx,cy]
        int x, int y, // only used for debugging
        rgba_t *color, int *pnIters, float *pIndex, fate_t *pFate // out params
        ) const;
    void recolor(struct im_info& ii) const;
};

#endif
