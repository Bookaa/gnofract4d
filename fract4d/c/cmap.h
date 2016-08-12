
#ifndef CMAP_H_
#define CMAP_H_

#include "color.h"

typedef enum
{
    TRANSFER_NONE,
    TRANSFER_LINEAR,
    TRANSFER_SIZE
} e_transferType;

typedef enum
{
    BLEND_LINEAR, 
    BLEND_CURVED, 
    BLEND_SINE, 
    BLEND_SPHERE_INCREASING, 
    BLEND_SPHERE_DECREASING
} e_blendType;


typedef enum
{ 
    RGB, 
    HSV_CCW, 
    HSV_CW
} e_colorType;

class ColorMap
{
public:
    ColorMap()
    {
        ncolors = 0;
    }
    virtual ~ColorMap() {}

    virtual bool init(int n_colors) = 0;
 
    virtual rgba_t lookup(double index) const = 0;

    rgba_t lookup_with_transfer(double index, int solid, int inside) const;
    rgba_t lookup_with_dca(int solid, int inside, double *colors) const;

 protected:
    int ncolors;
};

typedef struct 
{
    double left;
    double left_color[4];
    double right;
    double right_color[4];
    double mid;
    e_blendType bmode;
    e_colorType cmode;
} gradient_item_t;


class GradientColorMap: public ColorMap
{
 public:
    GradientColorMap() : ColorMap()
    {
        items = 0;
    }
    virtual ~GradientColorMap()
    {
        delete[] items;
    }

    virtual bool init(int n_colors);
    virtual rgba_t lookup(double index) const; 
    void set(int i,
             double left, double right, double mid,
             double *left_col,
             double *right_col,
             e_blendType bmode, e_colorType cmode);

 private:
    gradient_item_t *items;
};

extern void cmap_delete(ColorMap *cmap);


#endif /* CMAP_H_ */
