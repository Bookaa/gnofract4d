
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
    ColorMap();
    virtual ~ColorMap() {
        canary = 0xbaadf00d;
    }

    virtual bool init(int n_colors) = 0;
    virtual void set_solid(int which, int r, int g, int b, int a);
    virtual void set_transfer(int which, e_transferType type);
 
    virtual rgba_t lookup(double index) const = 0;

    rgba_t lookup_with_transfer(double index, int solid, int inside) const;
    rgba_t lookup_with_dca(int solid, int inside, double *colors) const;

 public:
    unsigned int canary;

 protected:
    int ncolors;
    rgba_t solids[2];
    e_transferType transfers[2];
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

    bool init(int n_colors);
    void set(int i,
             double left, double right, double mid,
             double *left_col,
             double *right_col,
             e_blendType bmode, e_colorType cmode);

    rgba_t lookup(double index) const; 
 private:
    gradient_item_t *items;

};

extern void cmap_delete(ColorMap *cmap);


#endif /* CMAP_H_ */
