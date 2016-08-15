/* Wrappers around C++ functions so they can be called from python The
   C code starts one or more non-Python threads which work out which
   points to calculate, and call the dynamically-compiled pointfunc C
   code created by the compiler for each pixel. 

   Results are reported back through a site object. There are 2 kinds,
   a synchronous site which calls back into python (used by
   command-line fractal.py script) and an async site which wraps a
   file descriptor into which we write simple messages. The GTK+ main
   loop then listens to the FD and performs operations in response to
   messages written to the file descriptor.
*/

#include "Python.h"

#include <dlfcn.h>
#include <pthread.h>

#include "assert.h"

#include <new>

#include "fract_stdlib.h"
#include "pf.h"
#include "cmap.h"
#include "fractFunc.h"
#include "image.h"


/* not sure why this isn't defined already */
#ifndef PyMODINIT_FUNC 
#define PyMODINIT_FUNC void
#endif

#define CMAP_NAME "/fract4d_stdlib.so"

#ifdef USE_GMP
#define MODULE_NAME "fract4dcgmp"
#include "gmp.h"
#else
#define MODULE_NAME "fract4dc"
#endif

/* 
 * pointfuncs
 */

PyObject *pymod=NULL;

typedef enum {
    DELTA_X,
    DELTA_Y,
    TOPLEFT
} vec_type_t;


static void
pf_unload(void *p)
{
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : SO : DEREF\n",p);
#endif
    dlclose(p);
}

struct pfHandle
{
    PyObject *pyhandle;
    pf_obj *pfo;

    // below init later :
    int maxiter;
    ColorMap *cmap;
    PyObject *pyim;
    double params[N_PARAMS];
} ;
static void
pf_delete(void *p)
{
    struct pfHandle *pfh = (struct pfHandle *)p;
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : PF : DTOR\n",pfh);
#endif
    pfh->pfo->vtbl->kill(pfh->pfo);
    Py_DECREF(pfh->pyhandle);

    if (pfh->cmap)
    {
        cmap_delete(pfh->cmap);
        pfh->cmap = 0;
    }
    if (pfh->pyim)
    {
        Py_DECREF(pfh->pyim);
        pfh->pyim = 0;
    }
    free(pfh);
}

static PyObject *
pf_load_and_create(PyObject *self, PyObject *args)
{
    /*if(!ensure_cmap_loaded())
    {
        return NULL;
    }*/

    char *so_filename;
    if(!PyArg_ParseTuple(args,"s",&so_filename))
    {
        return NULL;
    }

    void *dlHandle = dlopen(so_filename, RTLD_NOW);
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : SO : REF\n",dlHandle);
#endif
    if(NULL == dlHandle)
    {
        /* an error */
        PyErr_SetString(PyExc_ValueError,dlerror());
        return NULL;
    }

    PyObject *pyobj = PyCObject_FromVoidPtr(dlHandle,pf_unload);
    //return PyCObject_FromVoidPtr(dlHandle,pf_unload);

    pf_obj *(*pfn)(void); 
    pfn = (pf_obj *(*)(void))dlsym(dlHandle,"pf_new");
    if(NULL == pfn)
    {
        PyErr_SetString(PyExc_ValueError,dlerror());
        return NULL;
    }
    pf_obj *p = pfn();

    struct pfHandle *pfh = (pfHandle *)malloc(sizeof(struct pfHandle));
    pfh->pfo = p;
    pfh->pyhandle = pyobj;
    pfh->cmap = 0;
    pfh->pyim = 0;
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : PF : CTOR (%p)\n",pfh,pfh->pfo);
#endif

    // refcount module so it can't be unloaded before all funcs are gone
    //Py_INCREF(pyobj); 
    return PyCObject_FromVoidPtr(pfh,pf_delete);
}

void *
get_double_field(PyObject *pyitem, const char *name, double *pVal)
{
    PyObject *pyfield = PyObject_GetAttrString(pyitem,name);
    if(pyfield == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Bad segment object");
        return NULL;
    }
    *pVal = PyFloat_AsDouble(pyfield);
    Py_DECREF(pyfield);

    return pVal;
}

/* member 'name' of pyitem is a N-element list of doubles */
void *
get_double_array(PyObject *pyitem, const char *name, double *pVal, int n)
{
    PyObject *pyfield = PyObject_GetAttrString(pyitem,name);
    if(pyfield == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Bad segment object");
        return NULL;
    }

    if(!PySequence_Check(pyfield))
    {
        PyErr_SetString(PyExc_ValueError, "Bad segment object");
        Py_DECREF(pyfield);
        return NULL;
    }

    if(!(PySequence_Size(pyfield) == n))
    {
        PyErr_SetString(PyExc_ValueError, "Bad segment object");
        Py_DECREF(pyfield);
        return NULL;
    }

    for(int i = 0; i < n; ++i)
    {
        PyObject *py_subitem = PySequence_GetItem(pyfield,i);
        if(!py_subitem)
        {
            PyErr_SetString(PyExc_ValueError, "Bad segment object");
            Py_DECREF(pyfield);
            return NULL; 
        }
        *(pVal+i)=PyFloat_AsDouble(py_subitem);

        Py_DECREF(py_subitem);
    }

    Py_DECREF(pyfield);

    return pVal;
}

void *
get_int_field(PyObject *pyitem, const char *name, int *pVal)
{
    PyObject *pyfield = PyObject_GetAttrString(pyitem,name);
    if(pyfield == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "Bad segment object");
        return NULL;
    }
    *pVal = PyInt_AsLong(pyfield);
    Py_DECREF(pyfield);

    return pVal;
}

static ColorMap *
cmap_from_pyobject(PyObject *pyarray)
{
    int len, i;
    GradientColorMap *cmap;

    len = PySequence_Size(pyarray);
    if(len == 0)
    {
        PyErr_SetString(PyExc_ValueError,"Empty color array");
        return NULL;
    }

    cmap = new(std::nothrow)GradientColorMap();

    if(!cmap)
    {
        PyErr_SetString(PyExc_MemoryError,"Can't allocate colormap");
        return NULL;
    }
    if(! cmap->init(len))
    {
        PyErr_SetString(PyExc_MemoryError,"Can't allocate colormap array");
        delete cmap;
        return NULL;
    }

    for(i = 0; i < len; ++i)
    {
        double left, right, mid, left_col[4], right_col[4];
        int bmode, cmode;
        PyObject *pyitem = PySequence_GetItem(pyarray,i);
        if(!pyitem)
        {
            delete cmap;
            return NULL; 
        }

        if(!get_double_field(pyitem, "left", &left) ||
           !get_double_field(pyitem, "right", &right) ||
           !get_double_field(pyitem, "mid", &mid) ||
           !get_int_field(pyitem, "cmode", &cmode) ||
           !get_int_field(pyitem, "bmode", &bmode) ||
           !get_double_array(pyitem, "left_color", left_col, 4) ||
           !get_double_array(pyitem, "right_color", right_col, 4))
        {
            Py_DECREF(pyitem);
            delete cmap;
            return NULL;
        }
        
        cmap->set(i, left, right, mid,
                  left_col,right_col,
                  (e_blendType)bmode, (e_colorType)cmode);

        Py_DECREF(pyitem);
    }
    return cmap;
}

static bool
parse_posparams(PyObject *py_posparams, double *pos_params)
{
    // check and parse pos_params
    if(!PySequence_Check(py_posparams))
    {
        PyErr_SetString(PyExc_TypeError,
                        "Positional params should be an array of floats");
        return false;
    }

    int len = PySequence_Size(py_posparams);
    if(len != N_PARAMS)
    {
        PyErr_SetString(
            PyExc_ValueError,
            "Wrong number of positional params");
        return false;
    }
    
    for(int i = 0; i < N_PARAMS; ++i)
    {
        PyObject *pyitem = PySequence_GetItem(py_posparams,i);
        if(pyitem == NULL || !PyFloat_Check(pyitem))
        {
            PyErr_SetString(
                PyExc_ValueError,
                "All positional params must be floats");
            return false;
        }
        pos_params[i] = PyFloat_AsDouble(pyitem);
    }
    return true;
}

static s_param *
parse_params(PyObject *pyarray, int *plen)
{
    struct s_param *params;

    // check and parse fractal params
    if(!PySequence_Check(pyarray))
    {
        PyErr_SetString(PyExc_TypeError,
                        "parameters argument should be an array");
        return NULL;
    }

    int len = PySequence_Size(pyarray);
    if(len == 0)
    {
        params = (struct s_param *)malloc(sizeof(struct s_param));
        params[0].t = FLOAT;
        params[0].doubleval = 0.0;
    }
    else if(len > PF_MAXPARAMS)
    {
        PyErr_SetString(PyExc_ValueError,"Too many parameters");
        return NULL;
    }
    else
    {
        int i = 0;
        params = (struct s_param *)malloc(len * sizeof(struct s_param));
        if(!params) return NULL;
        for(i = 0; i < len; ++i)
        {
            PyObject *pyitem = PySequence_GetItem(pyarray,i);
            if(NULL == pyitem)
            {
                free(params);
                return NULL;
            }
            if(PyFloat_Check(pyitem))
            {
                params[i].t = FLOAT;
                params[i].doubleval = PyFloat_AsDouble(pyitem);
                //fprintf(stderr,"%d = float(%g)\n",i,params[i].doubleval);
            }
            else if(PyInt_Check(pyitem))
            {
                params[i].t = INT;
                params[i].intval = PyInt_AS_LONG(pyitem);
                //fprintf(stderr,"%d = int(%d)\n",i,params[i].intval);
            }
            else if(
                PyObject_HasAttrString(pyitem,"cobject") &&
                PyObject_HasAttrString(pyitem,"segments"))
            {
                // looks like a colormap. Either we already have an object, which we can use now,
                // or we need to construct one from a list of segments
                PyObject *pycob = PyObject_GetAttrString(pyitem,"cobject");
                if(pycob == Py_None || pycob == NULL)
                {
                    Py_XDECREF(pycob);
                    PyObject *pysegs = PyObject_GetAttrString(
                        pyitem,"segments");

                    ColorMap *cmap;
                    if (pysegs == Py_None || pysegs == NULL)
                    {
                        cmap = NULL;
                    }
                    else
                    {
                        cmap = cmap_from_pyobject(pysegs);
                    }
                    
                    Py_XDECREF(pysegs);

                    if(NULL == cmap)
                    {
                        PyErr_SetString(PyExc_ValueError, "Invalid colormap object");
                        free(params);
                        return NULL;
                    }

                    pycob = PyCObject_FromVoidPtr(
                        cmap, (void (*)(void *))cmap_delete);

                    if(NULL != pycob)
                    {
                        PyObject_SetAttrString(pyitem,"cobject",pycob);
                        // not quite correct, we are leaking some
                        // cmap objects 
                        Py_INCREF(pycob);
                    }
                }
                params[i].t = GRADIENT;
                params[i].gradient = PyCObject_AsVoidPtr(pycob);
                //fprintf(stderr,"%d = gradient(%p)\n",i,params[i].gradient);
                Py_XDECREF(pycob);
            }
            else if(
                PyObject_HasAttrString(pyitem,"_img"))
            {
                PyObject *pycob = PyObject_GetAttrString(pyitem,"_img");
                params[i].t = PARAM_IMAGE;
                params[i].image = PyCObject_AsVoidPtr(pycob);
                Py_XDECREF(pycob);
            }
            else
            {
                Py_XDECREF(pyitem);
                PyErr_SetString(
                    PyExc_ValueError,
                    "All params must be floats, ints, images or gradients");
                free(params);
                return NULL;
            }
            Py_XDECREF(pyitem);
        } 
    }
    *plen = len;
    return params;
}

static PyObject *
pf_init(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyarray, *py_posparams;

    if (!PyArg_ParseTuple(args,"OOO",&pyobj,&py_posparams, &pyarray))
    {
        return NULL;
    }
    if (!PyCObject_Check(pyobj))
    {
        PyErr_SetString(PyExc_ValueError,"Not a valid handle");
        return NULL;
    }

    struct pfHandle *pfh = (struct pfHandle *)PyCObject_AsVoidPtr(pyobj);

    // double pos_params[N_PARAMS];
    if (!parse_posparams(py_posparams, pfh->params))    // will write pfh->params
    {
        return NULL;
    }

    int len=0;
    struct s_param *params = parse_params(pyarray,&len);
    if (!params)
    {
        return NULL;
    }

    /*finally all args are assembled */
    pfh->pfo->vtbl->init(pfh->pfo, pfh->params, params, len);
    free(params);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pf_init2(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyarray, *pyim;
    int maxiter;

    if (!PyArg_ParseTuple(args,"OOiO",&pyobj,&pyarray,&maxiter,&pyim))
    {
        return NULL;
    }
    if (!PyCObject_Check(pyobj))
    {
        PyErr_SetString(PyExc_ValueError,"Not a valid handle");
        return NULL;
    }

    struct pfHandle *pfh = (struct pfHandle *)PyCObject_AsVoidPtr(pyobj);

    /* a gradient object:
       an array of objects with:
       float: left,right,mid 
       int: bmode, cmode
       [f,f,f,f] : left_color, right_color
    */
    if(!PySequence_Check(pyarray))
    {
        return NULL;
    }

    ColorMap *cmap = cmap_from_pyobject(pyarray);

    if(NULL == cmap)
    {
        return NULL;
    }
    pfh->cmap = cmap;
    pfh->maxiter = maxiter;
    pfh->pyim = pyim; Py_INCREF(pyim);

    Py_INCREF(Py_None);
    return Py_None;
}

struct calc_args
{
    double* params; // [N_PARAMS];
    int maxiter;
    pf_obj *pfo;
    ColorMap *cmap;
    IImage *im;
    int xoff,yoff,xres,yres;

    PyObject *pycmap, *pypfo, *pyim;
    calc_args()
    {
#ifdef DEBUG_CREATION
        fprintf(stderr, "%p : CA : CTOR\n", this);
#endif
        pycmap = NULL;
        pypfo = NULL;
        pyim = NULL;
        maxiter = 1024;
        // nThreads = 1;
    }

    void set_pfo(PyObject *pypfo_)
    {
        pypfo = pypfo_;

        pfHandle* pfh = (pfHandle *)PyCObject_AsVoidPtr(pypfo);
        this->params = pfh->params;
        this->cmap = pfh->cmap;
        this->maxiter = pfh->maxiter;
        this->im = (IImage *)PyCObject_AsVoidPtr(pfh->pyim);

        pfo = pfh->pfo;
        Py_XINCREF(pypfo);
    }

    ~calc_args()
    {
        Py_XDECREF(pycmap);
        Py_XDECREF(pypfo);
        Py_XDECREF(pyim);
    }
};


static calc_args *
parse_calc_args(PyObject *args, PyObject *kwds)
{
    calc_args *cargs = new calc_args();

    static const char *kwlist[] = { "pfo", "xoff", "yoff", "xres", "yres", NULL};

    PyObject *pypfo;
    if(!PyArg_ParseTupleAndKeywords(args, kwds, "O|iiii", const_cast<char **>(kwlist), &pypfo, 
                                    &cargs->xoff, &cargs->yoff, &cargs->xres, &cargs->yres))
    {
error:
        delete cargs;
        return NULL;
    }

    cargs->set_pfo(pypfo);

    if(!cargs->cmap || !cargs->pfo || !cargs->im)
    {
        PyErr_SetString(PyExc_ValueError, "bad argument passed to calc");
        goto error;
    }

    if(!cargs->im->ok())
    {
        PyErr_SetString(PyExc_MemoryError, "image not allocated"); 
        goto error;
    }

    return cargs;
}

void calc_4(d *params, int maxiter, pf_obj *pfo, ColorMap *cmap, IImage *im);

static PyObject *
pycalc(PyObject *self, PyObject *args, PyObject *kwds)
{
    calc_args *cargs = parse_calc_args(args, kwds);
    if (NULL == cargs)
    {
        return NULL;
    }
    if (true)
    {
        int xtotalsize = cargs->im->totalXres();
        int ytotalsize = cargs->im->totalYres();

        cargs->im->set_resolution(cargs->xres, cargs->yres, xtotalsize, ytotalsize);

        cargs->im->set_offset(cargs->xoff, cargs->yoff);
    }
    {
        calc_4(cargs->params, cargs->maxiter, cargs->pfo, cargs->cmap, cargs->im);

        delete cargs;
    }

    Py_INCREF(Py_None);
    
    return Py_None;
}

static void
image_delete(IImage *image)
{
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : IM : DTOR\n",image);
#endif
    delete image;
}

static PyObject *
image_create(PyObject *self, PyObject *args)
{
    int x, y;
    int totalx = -1, totaly = -1;
    if(!PyArg_ParseTuple(args,"ii|ii",&x,&y,&totalx, &totaly))
    { 
        return NULL;
    }

    IImage *i = new image();

    i->set_resolution(x,y,totalx, totaly);

    if(! i->ok())
    {
        PyErr_SetString(PyExc_MemoryError, "Image too large");
        delete i;
        return NULL;
    }

#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : IM : CTOR\n",i);
#endif

    PyObject *pyret = PyCObject_FromVoidPtr(i,(void (*)(void *))image_delete);

    return pyret;
}

static PyObject *
bookaa_set_offset_resolution(PyObject *self, PyObject *args)
{
    int xoff, yoff, xres, yres;
    PyObject *pyim;
    if(!PyArg_ParseTuple(args,"Oiiii",&pyim,&xoff,&yoff,&xres, &yres))
    { 
        return NULL;
    }

    IImage *i = (IImage *)PyCObject_AsVoidPtr(pyim);

    int xtotalsize = i->totalXres();
    int ytotalsize = i->totalYres();

    i->set_resolution(xres, yres, xtotalsize, ytotalsize);
    i->set_offset(xoff, yoff);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_dims(PyObject *self, PyObject *args)
{
    PyObject *pyim;

    if(!PyArg_ParseTuple(args,"O",&pyim))
    { 
        return NULL;
    }

    IImage *i = (IImage *)PyCObject_AsVoidPtr(pyim);
    if(NULL == i)
    {
        return NULL;
    }

    int xsize, ysize, xoffset, yoffset, xtotalsize, ytotalsize;
    xsize = i->Xres();
    ysize = i->Yres();
    xoffset = i->Xoffset();
    yoffset = i->Yoffset();
    xtotalsize = i->totalXres();
    ytotalsize = i->totalYres();

    PyObject *pyret = Py_BuildValue(
        "(iiiiii)", xsize,ysize,xtotalsize, ytotalsize, xoffset, yoffset);

    return pyret;
}

static PyObject *
image_save_all(PyObject *self,PyObject *args)
{
    PyObject *pyim;
    PyObject *pyFP;
    if(!PyArg_ParseTuple(args,"OO",&pyim,&pyFP))
    {
        return NULL;
    }

    if(!PyFile_Check(pyFP))
    {
        return NULL;
    }

    image *i = (image *)PyCObject_AsVoidPtr(pyim);

    FILE *fp = PyFile_AsFile(pyFP);

    if(!fp || !i)
    {
        PyErr_SetString(PyExc_ValueError, "Bad arguments");
        return NULL;
    }
    
    ImageWriter *writer = ImageWriter::create(FILE_TYPE_PNG, fp, i);
    if(NULL == writer)
    {
        PyErr_SetString(PyExc_ValueError, "Unsupported file type");
        return NULL;
    }

    // return PyCObject_FromVoidPtr(writer, (void (*)(void *))image_writer_delete);

    writer->save_header();

    writer->save_tile();

    writer->save_footer();

    delete writer;

    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef PfMethods[] = {
    {"pf_load_and_create",  pf_load_and_create, METH_VARARGS, "Load a new point function shared library, and Create a new point function"},
    {"pf_init", pf_init, METH_VARARGS, "Init a point function"},
    {"pf_init2", pf_init2, METH_VARARGS, "Init a point function"},

    { "image_create", image_create, METH_VARARGS, "Create a new image buffer"},
    { "image_dims", image_dims, METH_VARARGS, "get a tuple containing image's dimensions"},
    { "bookaa_set_offset_resolution", bookaa_set_offset_resolution, METH_VARARGS, "bookaa_set_offset_resolution"},

    { "image_save_all", image_save_all, METH_VARARGS, "image_sav_all" },

    { "calc", (PyCFunction) pycalc, METH_VARARGS | METH_KEYWORDS, "Calculate a fractal image"},

    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
#ifdef USE_GMP
initfract4dcgmp(void)
#else
initfract4dc(void)
#endif
{
    pymod = Py_InitModule(MODULE_NAME, PfMethods);

#ifdef THREADS
    PyEval_InitThreads();
#endif

#ifdef USE_GMP
    mpf_t x;
    mpf_init(x);
#endif
    /* expose some constants */
    PyModule_AddIntConstant(pymod, "CALC_DONE", GF4D_FRACTAL_DONE);
    PyModule_AddIntConstant(pymod, "CALC_CALCULATING", GF4D_FRACTAL_CALCULATING);
    PyModule_AddIntConstant(pymod, "CALC_DEEPENING", GF4D_FRACTAL_DEEPENING);
    PyModule_AddIntConstant(pymod, "CALC_ANTIALIASING", GF4D_FRACTAL_ANTIALIASING);
    PyModule_AddIntConstant(pymod, "CALC_PAUSED", GF4D_FRACTAL_PAUSED);

    PyModule_AddIntConstant(pymod, "AA_NONE", AA_NONE);
    PyModule_AddIntConstant(pymod, "AA_FAST", AA_FAST);
    PyModule_AddIntConstant(pymod, "AA_BEST", AA_BEST);

    PyModule_AddIntConstant(pymod, "RENDER_TWO_D", RENDER_TWO_D);
    PyModule_AddIntConstant(pymod, "RENDER_LANDSCAPE", RENDER_LANDSCAPE);
    PyModule_AddIntConstant(pymod, "RENDER_THREE_D", RENDER_THREE_D);

    PyModule_AddIntConstant(pymod, "DRAW_GUESSING", DRAW_GUESSING);
    PyModule_AddIntConstant(pymod, "DRAW_TO_DISK", DRAW_TO_DISK);

    PyModule_AddIntConstant(pymod, "DELTA_X", DELTA_X);
    PyModule_AddIntConstant(pymod, "DELTA_Y", DELTA_Y);
    PyModule_AddIntConstant(pymod, "TOPLEFT", TOPLEFT);

    /* cf image_dims */
    PyModule_AddIntConstant(pymod, "IMAGE_WIDTH", 0);
    PyModule_AddIntConstant(pymod, "IMAGE_HEIGHT", 1);
    PyModule_AddIntConstant(pymod, "IMAGE_TOTAL_WIDTH", 2);
    PyModule_AddIntConstant(pymod, "IMAGE_TOTAL_HEIGHT", 3);
    PyModule_AddIntConstant(pymod, "IMAGE_XOFFSET", 4);
    PyModule_AddIntConstant(pymod, "IMAGE_YOFFSET", 5);

    /* image type consts */
    PyModule_AddIntConstant(pymod, "FILE_TYPE_TGA", FILE_TYPE_TGA);
    PyModule_AddIntConstant(pymod, "FILE_TYPE_PNG", FILE_TYPE_PNG);
    PyModule_AddIntConstant(pymod, "FILE_TYPE_JPG", FILE_TYPE_JPG);
}
