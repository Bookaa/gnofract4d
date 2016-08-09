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
void *cmap_module_handle=NULL;

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
    #ifndef STATIC_CALC    
    dlclose(p);
    #endif
}

static int 
ensure_cmap_loaded()
{
    char cwd[PATH_MAX+1];
    // load the cmap module so fract funcs we compile later
    // can call its methods
    if(NULL != cmap_module_handle)
    {
        return 1; // already loaded
    }

    char *filename = PyModule_GetFilename(pymod);
    //fprintf(stderr,"base name: %s\n",filename);
    char *path_end = strrchr(filename,'/');
    if(path_end == NULL)
    {
        filename = getcwd(cwd,sizeof(cwd));
        path_end = filename + strlen(filename);
    }

    int path_len = strlen(filename) - strlen(path_end);
    int len = path_len + strlen(CMAP_NAME);

    char *new_filename = (char *)malloc(len+1);
    strncpy(new_filename, filename, path_len);
    new_filename[path_len] = '\0';
    strcat(new_filename, CMAP_NAME);
    //fprintf(stderr,"Filename: %s\n", new_filename);

    cmap_module_handle = dlopen(new_filename, RTLD_GLOBAL | RTLD_NOW);
    if(NULL == cmap_module_handle)
    {
        /* an error */
        PyErr_SetString(PyExc_ValueError, dlerror());
        return 0;
    }
    return 1;
}

static PyObject *
pf_load(PyObject *self, PyObject *args)
{
    #ifdef STATIC_CALC
    Py_INCREF(Py_None);
    return Py_None;
    #else
    if(!ensure_cmap_loaded())
    {
        return NULL;
    }

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
    return PyCObject_FromVoidPtr(dlHandle,pf_unload);
    #endif
}

struct pfHandle
{
    PyObject *pyhandle;
    pf_obj *pfo;
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
    free(pfh);
}

static PyObject *
pf_create(PyObject *self, PyObject *args)
{
    struct pfHandle *pfh = (pfHandle *)malloc(sizeof(struct pfHandle));
    void *dlHandle;
    pf_obj *(*pfn)(void); 

    PyObject *pyobj;
#ifdef STATIC_CALC
    pf_obj *p = pf_new();
    pyobj = Py_None;
#else

    if(!PyArg_ParseTuple(args,"O",&pyobj))
    {
        return NULL;
    }
    if(!PyCObject_Check(pyobj))
    {
        PyErr_SetString(PyExc_ValueError,"Not a valid handle");
        return NULL;
    }

    dlHandle = PyCObject_AsVoidPtr(pyobj);
    pfn = (pf_obj *(*)(void))dlsym(dlHandle,"pf_new");
    if(NULL == pfn)
    {
        PyErr_SetString(PyExc_ValueError,dlerror());
        return NULL;
    }
    pf_obj *p = pfn();
#endif
    pfh->pfo = p;
    pfh->pyhandle = pyobj;
#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : PF : CTOR (%p)\n",pfh,pfh->pfo);
#endif
    // refcount module so it can't be unloaded before all funcs are gone
    Py_INCREF(pyobj); 
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

static PyObject *
cmap_create_gradient(PyObject *self, PyObject *args)
{
    /* args = a gradient object:
       an array of objects with:
       float: left,right,mid 
       int: bmode, cmode
       [f,f,f,f] : left_color, right_color
    */
    PyObject *pyarray, *pyret;

    if(!PyArg_ParseTuple(args,"O",&pyarray))
    {
        return NULL;
    }

    if(!PySequence_Check(pyarray))
    {
        return NULL;
    }
    
    ColorMap *cmap = cmap_from_pyobject(pyarray);

    if(NULL == cmap)
    {
        return NULL;
    }

    pyret = PyCObject_FromVoidPtr(cmap,(void (*)(void *))cmap_delete);

    return pyret;
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
    struct s_param *params;
    struct pfHandle *pfh;
    double pos_params[N_PARAMS];

    if(!PyArg_ParseTuple(
           args,"OOO",&pyobj,&py_posparams, &pyarray))
    {
        return NULL;
    }
    if(!PyCObject_Check(pyobj))
    {
        PyErr_SetString(PyExc_ValueError,"Not a valid handle");
        return NULL;
    }

    pfh = (struct pfHandle *)PyCObject_AsVoidPtr(pyobj);

    if(!parse_posparams(py_posparams, pos_params))
    {
        return NULL;
    }

    int len=0;
    params = parse_params(pyarray,&len);
    if(!params)
    {
        return NULL;
    }

    /*finally all args are assembled */
    pfh->pfo->vtbl->init(pfh->pfo,pos_params,params,len);
    free(params);

    Py_INCREF(Py_None);
    return Py_None;
}


/*
 * cmaps
 */
static PyObject *
pycmap_set_solid(PyObject *self, PyObject *args)
{
    PyObject *pycmap;
    int which,r,g,b,a;
    ColorMap *cmap;

    if(!PyArg_ParseTuple(args,"Oiiiii",&pycmap,&which,&r,&g,&b,&a))
    {
        return NULL;
    }

    cmap = (ColorMap *)PyCObject_AsVoidPtr(pycmap);
    if(!cmap)
    {
        return NULL;
    }

    cmap->set_solid(which,r,g,b,a);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
pycmap_set_transfer(PyObject *self, PyObject *args)
{
    PyObject *pycmap;
    int which;
    e_transferType transfer;
    ColorMap *cmap;

    if(!PyArg_ParseTuple(args,"Oii",&pycmap,&which,&transfer))
    {
        return NULL;
    }

    cmap = (ColorMap *)PyCObject_AsVoidPtr(pycmap);
    if(!cmap)
    {
        return NULL;
    }

    cmap->set_transfer(which,transfer);

    Py_INCREF(Py_None);
    return Py_None;
}
 
static PyObject *
cmap_pylookup(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyret;
    double d;
    rgba_t color;
    ColorMap *cmap;

    if(!PyArg_ParseTuple(args,"Od", &pyobj, &d))
    {
        return NULL;
    }

    cmap = (ColorMap *)PyCObject_AsVoidPtr(pyobj);
    if(!cmap)
    {
        return NULL;
    }

    color = cmap->lookup(d);
    
    pyret = Py_BuildValue("iiii",color.r,color.g,color.b,color.a);

    return pyret;
}

static PyObject *
cmap_pylookup_with_flags(PyObject *self, PyObject *args)
{
    PyObject *pyobj, *pyret;
    double d;
    rgba_t color;
    ColorMap *cmap;
    int inside;
    int solid;

    if(!PyArg_ParseTuple(args,"Odii", &pyobj, &d, &solid, &inside))
    {
        return NULL;
    }

    cmap = (ColorMap *)PyCObject_AsVoidPtr(pyobj);
    if(!cmap)
    {
        return NULL;
    }

    color = cmap->lookup_with_transfer(d,solid,inside);
    
    pyret = Py_BuildValue("iiii",color.r,color.g,color.b,color.a);

    return pyret;
}

#ifdef THREADS
#define GET_LOCK PyGILState_STATE gstate; gstate = PyGILState_Ensure()
#define RELEASE_LOCK PyGILState_Release(gstate)
#else
#define GET_LOCK
#define RELEASE_LOCK
#endif

class PySite :public IFractalSite
{
public:
    PySite(PyObject *site_)
        {
            site = site_;

            has_pixel_changed_method = 
                PyObject_HasAttrString(site,"pixel_changed");

#ifdef DEBUG_CREATION
            fprintf(stderr,"%p : SITE : CTOR\n",this);
#endif

            // Don't incref, that causes a loop with parent fractal
            //Py_INCREF(site);
        }

    virtual void iters_changed(int numiters)
        {
            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("iters_changed"),
                const_cast<char *>("i"),
                numiters);
            Py_XDECREF(ret);
            RELEASE_LOCK;
        }
    
    virtual void tolerance_changed(double tolerance)
        {
            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("tolerance_changed"),
                const_cast<char *>("d"),
                tolerance);
            Py_XDECREF(ret);
            RELEASE_LOCK;
        }
    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int y1, int x2, int y2)
        {
            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("image_changed"),
                const_cast<char *>("iiii"),
                x1,y1,x2,y2);
            Py_XDECREF(ret);
            RELEASE_LOCK;
        }
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress)
        {
            double d = (double)progress;

            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("progress_changed"),
                const_cast<char *>("d"),
                d);
            Py_XDECREF(ret);
            RELEASE_LOCK;
        }

    virtual void stats_changed(pixel_stat_t& stats)
        {
            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("stats_changed"),
                const_cast<char *>("[kkkkkkkkkk]"),
                stats.s[0], stats.s[1], stats.s[2],stats.s[3],stats.s[4],
                stats.s[5], stats.s[6], stats.s[7],stats.s[8],stats.s[9]);
            Py_XDECREF(ret);
            RELEASE_LOCK;                       
        }

    // one of the status values above
    virtual void status_changed(int status_val)
        {
            assert(this != NULL && site != NULL);
            //fprintf(stderr,"sc: %p %p\n",this,this->status_changed_cb);

            GET_LOCK;
            PyObject *ret = PyObject_CallMethod(
                site,
                const_cast<char *>("status_changed"),
                const_cast<char *>("i"), 
                status_val);

            if(PyErr_Occurred())
            {
                fprintf(stderr,"bad status 2\n");
                PyErr_Print();
            }
            Py_XDECREF(ret);
            RELEASE_LOCK;
        }

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted()
        {
            GET_LOCK;
            PyObject *pyret = PyObject_CallMethod(
                site,
                const_cast<char *>("is_interrupted"),NULL);

            bool ret = false;
            if(pyret != NULL && PyInt_Check(pyret))
            {
                long i = PyInt_AsLong(pyret);
                //fprintf(stderr,"ret: %ld\n",i);
                ret = (i != 0);
            }

            Py_XDECREF(pyret);
            RELEASE_LOCK;
            return ret;
        }

    // pixel changed
    virtual void pixel_changed(
        const double *params, int maxIters, int nNoPeriodIters,
        int x, int y, int aa,
        double dist, int fate, int nIters,
        int r, int g, int b, int a) 
        {
            if(has_pixel_changed_method)
            {
                GET_LOCK;
                PyObject *pyret = PyObject_CallMethod(
                    site,
                    const_cast<char *>("pixel_changed"),
                    const_cast<char *>("(dddd)iiiiidiiiiii"),
                    params[0],params[1],params[2],params[3],
                    x,y,aa,
                    maxIters,nNoPeriodIters,
                    dist,fate,nIters,
                    r,g,b,a);

                Py_XDECREF(pyret);
                RELEASE_LOCK;
            }
        };
    virtual void interrupt() 
        {
            // FIXME? interrupted = true;
        }
    
    virtual void start(calc_args *tid_)
        {
            tid = (pthread_t)tid_;
        }

    virtual void wait()
        {
            pthread_join(tid,NULL);
        }

    ~PySite()
        {
#ifdef DEBUG_CREATION
            fprintf(stderr,"%p : SITE : DTOR\n",this);
#endif
            //Py_DECREF(site);
        }

    //PyThreadState *state;
private:
    PyObject *site;
    bool has_pixel_changed_method;
    pthread_t tid;
};

typedef enum
{
    ITERS,
    IMAGE,
    PROGRESS,
    STATUS,
    PIXEL,
    TOLERANCE,
    STATS,
} msg_type_t;
    
struct calc_args
{
    double params[N_PARAMS];
    int eaa, maxiter; //, nThreads;
    int auto_deepen, yflip, periodicity, dirty;
    int auto_tolerance;
    double tolerance;
    int async, warp_param;
    render_type_t render_type;
    pf_obj *pfo;
    ColorMap *cmap;
    IImage *im;
    IFractalSite *site;

    PyObject *pycmap, *pypfo, *pyim, *pysite;
    calc_args()
    {
#ifdef DEBUG_CREATION
        fprintf(stderr, "%p : CA : CTOR\n", this);
#endif
        pycmap = NULL;
        pypfo = NULL;
        pyim = NULL;
        pysite = NULL;
        dirty = 1;
        periodicity = true;
        yflip = false;
        auto_deepen = false;
        auto_tolerance = false;
        tolerance = 1.0E-9;
        eaa = AA_NONE;
        maxiter = 1024;
        // nThreads = 1;
        render_type = RENDER_TWO_D;
        async = false;
        warp_param = -1;
    }

    void set_cmap(PyObject *pycmap_)
    {
        pycmap = pycmap_;
        cmap = (ColorMap *)PyCObject_AsVoidPtr(pycmap);
        Py_XINCREF(pycmap);
    }

    void set_pfo(PyObject *pypfo_)
    {
        pypfo = pypfo_;

        pfo = ((pfHandle *)PyCObject_AsVoidPtr(pypfo))->pfo;
        Py_XINCREF(pypfo);
    }

    void set_im(PyObject *pyim_)
    {
        pyim = pyim_;
        im = (IImage *)PyCObject_AsVoidPtr(pyim);
        Py_XINCREF(pyim);
    }

    void set_site(PyObject *pysite_)
    {
        pysite = pysite_;
        site = (IFractalSite *)PyCObject_AsVoidPtr(pysite);
        Py_XINCREF(pysite);
    }

    ~calc_args()
    {
#ifdef DEBUG_CREATION
        fprintf(stderr, "%p : CA : DTOR\n", this);
#endif
        Py_XDECREF(pycmap);
        Py_XDECREF(pypfo);
        Py_XDECREF(pyim);
        Py_XDECREF(pysite);
    }
};

// write the callbacks to a file descriptor
class FDSite :public IFractalSite
{
public:
    FDSite(int fd_) : fd(fd_), tid((pthread_t)0),
        interrupted(false), params(NULL)
    {
#ifdef DEBUG_CREATION
        fprintf(stderr, "%p : FD : CTOR\n", this);
#endif
        pthread_mutex_init(&write_lock, NULL);
    }

    inline void send(msg_type_t type, int size, void *buf)
    {
        pthread_mutex_lock(&write_lock);
        if (write(fd, &type, sizeof(type)))
        {};
        if (write(fd, &size, sizeof(size)))
        {};
        if (write(fd, buf, size))
        {};
        pthread_mutex_unlock(&write_lock);
    }
    virtual void iters_changed(int numiters)
    {
        send(ITERS, sizeof(int), &numiters);
    }
    virtual void tolerance_changed(double tolerance)
    {
        send(TOLERANCE, sizeof(tolerance), &tolerance);
    }

    // we've drawn a rectangle of image
    virtual void image_changed(int x1, int y1, int x2, int y2)
    {
        if (!interrupted)
        {
            int buf[4] = { x1, y1, x2, y2 };
            send(IMAGE, sizeof(buf), &buf[0]);
        }
    }
    // estimate of how far through current pass we are
    virtual void progress_changed(float progress)
    {
        if (!interrupted)
        {
            int percentdone = (int)(100.0 * progress);
            send(PROGRESS, sizeof(percentdone), &percentdone);
        }
    }

    virtual void stats_changed(pixel_stat_t& stats)
    {
        if (!interrupted)
        {
            send(STATS, sizeof(stats), &stats);
        }

    }

    // one of the status values above
    virtual void status_changed(int status_val)
    {
        send(STATUS, sizeof(status_val), &status_val);
    }

    // return true if we've been interrupted and are supposed to stop
    virtual bool is_interrupted()
    {
        //fprintf(stderr,"int: %d\n",interrupted);
        return interrupted;
    }

    // pixel changed
    virtual void pixel_changed(
        const double *params, int maxIters, int nNoPeriodIters,
        int x, int y, int aa,
        double dist, int fate, int nIters,
        int r, int g, int b, int a)
    {
        /*
        fprintf(stderr,"pixel: <%g,%g,%g,%g>(%d,%d,%d) = (%g,%d,%d)\n",
               params[0],params[1],params[2],params[3],
               x,y,aa,dist,fate,nIters);
        */
        return; // FIXME
    };

    virtual void interrupt()
    {
#ifdef DEBUG_THREADS
        fprintf(stderr, "%p : CA : INT(%p)\n", this, tid);
#endif
        interrupted = true;
    }

    virtual void start(calc_args *params_)
    {
#ifdef DEBUG_THREADS
        fprintf(stderr, "clear interruption\n");
#endif
        interrupted = false;
        params = params_;
    }

    virtual void set_tid(pthread_t tid_)
    {
#ifdef DEBUG_THREADS
        fprintf(stderr, "%p : CA : SET(%p)\n", this, tid_);
#endif
        tid = tid_;
    }

    virtual void wait()
    {
        if (tid != 0)
        {
#ifdef DEBUG_THREADS
            fprintf(stderr, "%p : CA : WAIT(%p)\n", this, tid);
#endif
            pthread_join(tid, NULL);
        }
    }
    ~FDSite()
    {
#ifdef DEBUG_CREATION
        fprintf(stderr, "%p : FD : DTOR\n", this);
#endif
        close(fd);
    }
private:
    int fd;
    pthread_t tid;
    volatile bool interrupted;
    calc_args *params;
    pthread_mutex_t write_lock;
};

static void
site_delete(IFractalSite *site)
{
    delete site;
}

struct ffHandle
{
    PyObject *pyhandle;
    fractFunc *ff;
} ;


static PyObject *
pyfdsite_create(PyObject *self, PyObject *args)
{
    int fd;
    if(!PyArg_ParseTuple(args,"i", &fd))
    {
        return NULL;
    }

    IFractalSite *site = new FDSite(fd);

    PyObject *pyret = PyCObject_FromVoidPtr(site,(void (*)(void *))site_delete);

    return pyret;
}


static calc_args *
parse_calc_args(PyObject *args, PyObject *kwds)
{
    PyObject *pyparams, *pypfo, *pycmap, *pyim, *pysite;
    calc_args *cargs = new calc_args();
    double *p = NULL;

    static const char *kwlist[] = {
        "image",
        "site",
        "pfo",
        "cmap",
        "params",
        //"antialias",
        "maxiter",
        //"yflip",
            //"nthreads",
        //"auto_deepen",
        //"periodicity",
        //"render_type",
        //"dirty", 
        //"async",
        //"warp_param",
        //"tolerance",
        //"auto_tolerance",
        NULL};

    if(!PyArg_ParseTupleAndKeywords(
           args,
           kwds,
           "OOOOO|i",
           const_cast<char **>(kwlist),

           &pyim, &pysite,
           &pypfo,&pycmap,
           &pyparams,
           //&cargs->eaa,
           &cargs->maxiter
           //&cargs->yflip,
            // &cargs->nThreads,
           //&cargs->auto_deepen,
           //&cargs->periodicity,
           //&cargs->render_type,
           //&cargs->dirty,
           //&cargs->async,
           //&cargs->warp_param,
           //&cargs->tolerance,
           //&cargs->auto_tolerance
           ))
    {
        goto error;
    }
    cargs->dirty = 0;
    cargs->async = 0;
    cargs->warp_param = -1;
    cargs->render_type = RENDER_TWO_D;
    cargs->tolerance = 0.0;
    cargs->auto_tolerance = 1;
    cargs->auto_deepen = 1;
    cargs->periodicity = 1;
    cargs->yflip = 0;
    cargs->eaa = 1;


    p = cargs->params;
    if(!PyList_Check(pyparams) || PyList_Size(pyparams) != N_PARAMS)
    {
        PyErr_SetString(PyExc_ValueError, "bad parameter list");
        goto error;
    }

    for(int i = 0; i < N_PARAMS; ++i)
    {
        PyObject *elt = PyList_GetItem(pyparams, i);
        if(!PyFloat_Check(elt))
        {
            PyErr_SetString(PyExc_ValueError, "a param is not a float");
            goto error;
        }

        p[i] = PyFloat_AsDouble(elt);
    }

    cargs->set_cmap(pycmap);
    cargs->set_pfo(pypfo);
    cargs->set_im(pyim);
    cargs->set_site(pysite);
    if(!cargs->cmap || !cargs->pfo || 
       !cargs->im   || !cargs->site)
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

error:
    delete cargs;
    return NULL;
}

static PyObject *
pycalc(PyObject *self, PyObject *args, PyObject *kwds)
{
    calc_args *cargs = parse_calc_args(args, kwds);
    if (NULL == cargs)
    {
        return NULL;
    }

    {
        Py_BEGIN_ALLOW_THREADS
        // synchronous
        printf("call calc 1728 \n");
        calc_4(cargs->params,
             cargs->maxiter,
             cargs->pfo,
             cargs->cmap,
             cargs->im,
             cargs->site);

        delete cargs;
        Py_END_ALLOW_THREADS
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
image_resize(PyObject *self, PyObject *args)
{
    int x, y;
    int totalx=-1, totaly=-1;
    PyObject *pyim;

    if(!PyArg_ParseTuple(args,"Oiiii",&pyim,&x,&y,&totalx,&totaly))
    { 
        return NULL;
    }

    IImage *i = (IImage *)PyCObject_AsVoidPtr(pyim);
    if(NULL == i)
    {
        return NULL;
    }

    i->set_resolution(x,y,totalx,totaly);

    if(! i->ok())
    {
        PyErr_SetString(PyExc_MemoryError, "Image too large");
        return NULL;
    }

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
image_set_offset(PyObject *self, PyObject *args)
{
    int x, y;
    PyObject *pyim;

    if(!PyArg_ParseTuple(args,"Oii",&pyim,&x,&y))
    { 
        return NULL;
    }

    IImage *i = (IImage *)PyCObject_AsVoidPtr(pyim);
    if(NULL == i)
    {
        return NULL;
    }

    bool ok = i->set_offset(x,y);
    if(!ok)
    {
        PyErr_SetString(PyExc_ValueError, "Offset out of bounds");
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_clear(PyObject *self, PyObject *args)
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

    i->clear();

    Py_INCREF(Py_None);
    return Py_None;
}

static void
image_writer_delete(ImageWriter *im)
{
    delete im;
}

static PyObject *
image_writer_create(PyObject *self,PyObject *args)
{
    PyObject *pyim;
    PyObject *pyFP;
    int file_type;
    if(!PyArg_ParseTuple(args,"OOi",&pyim,&pyFP,&file_type))
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
    
    ImageWriter *writer = ImageWriter::create((image_file_t)file_type, fp, i);
    if(NULL == writer)
    {
        PyErr_SetString(PyExc_ValueError, "Unsupported file type");
        return NULL;
    }

    return PyCObject_FromVoidPtr(
        writer, (void (*)(void *))image_writer_delete);
}

static PyObject *
image_read(PyObject *self,PyObject *args)
{
    PyObject *pyim;
    PyObject *pyFP;
    int file_type;
    if(!PyArg_ParseTuple(args,"OOi",&pyim,&pyFP,&file_type))
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
    
    ImageReader *reader = ImageReader::create((image_file_t)file_type, fp, i);
    //if(!reader->ok())
    //{
    //  PyErr_SetString(PyExc_IOError, "Couldn't create image reader");
    //  delete reader;
    //  return NULL;
    //}

    if(!reader->read())
    {
        PyErr_SetString(PyExc_IOError, "Couldn't read image contents");
        delete reader;
        return NULL;
    }
    delete reader;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_save_header(PyObject *self,PyObject *args)
{
    PyObject *pyimwriter;
    if(!PyArg_ParseTuple(args,"O",&pyimwriter))
    {
        return NULL;
    }

    ImageWriter *i = (ImageWriter *)PyCObject_AsVoidPtr(pyimwriter);

    if(!i || !i->save_header())
    {
        PyErr_SetString(PyExc_IOError, "Couldn't save file header");
        return NULL;
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}
    
static PyObject *
image_save_tile(PyObject *self,PyObject *args)
{
    PyObject *pyimwriter;
    if(!PyArg_ParseTuple(args,"O",&pyimwriter))
    {
        return NULL;
    }

    ImageWriter *i = (ImageWriter *)PyCObject_AsVoidPtr(pyimwriter);

    if(!i || !i->save_tile())
    {
        PyErr_SetString(PyExc_IOError, "Couldn't save image tile");
        return NULL;
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_save_footer(PyObject *self,PyObject *args)
{
    PyObject *pyimwriter;
    if(!PyArg_ParseTuple(args,"O",&pyimwriter))
    {
        return NULL;
    }

    ImageWriter *i = (ImageWriter *)PyCObject_AsVoidPtr(pyimwriter);

    if(!i || !i->save_footer())
    {
        PyErr_SetString(PyExc_IOError, "Couldn't save image footer");
        return NULL;
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
image_buffer(PyObject *self, PyObject *args)
{
    PyObject *pyim;
    PyObject *pybuf;

    int x=0,y=0;
    if(!PyArg_ParseTuple(args,"O|ii",&pyim,&x,&y))
    {
        return NULL;
    }

    image *i = (image *)PyCObject_AsVoidPtr(pyim);

#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : IM : BUF\n",i);
#endif

    if(!i || ! i->ok())
    {
        PyErr_SetString(PyExc_MemoryError, "image not allocated");
        return NULL;
    }

    if(x < 0 || x >= i->Xres() || y < 0 || y >= i->Yres())
    {
        PyErr_SetString(PyExc_ValueError,"request for buffer outside image bounds");
        return NULL;
    }
    int offset = 3 * (y * i->Xres() + x);
    assert(offset > -1 && offset < i->bytes());
    pybuf = PyBuffer_FromReadWriteMemory(i->getBuffer()+offset,i->bytes()-offset);
    Py_XINCREF(pybuf);
    //Py_XINCREF(pyim);

    return pybuf;
}

static PyObject *
image_fate_buffer(PyObject *self, PyObject *args)
{
    PyObject *pyim;
    PyObject *pybuf;

    int x=0,y=0;
    if(!PyArg_ParseTuple(args,"O|ii",&pyim,&x,&y))
    {
        return NULL;
    }

    image *i = (image *)PyCObject_AsVoidPtr(pyim);

#ifdef DEBUG_CREATION
    fprintf(stderr,"%p : IM : BUF\n",i);
#endif

    if(NULL == i)
    {
        PyErr_SetString(PyExc_ValueError,
                        "Bad image object");
        return NULL;
    }

    if(x < 0 || x >= i->Xres() || y < 0 || y >= i->Yres())
    {
        PyErr_SetString(PyExc_ValueError,"request for buffer outside image bounds");
        return NULL;
    }
    int index = i->index_of_subpixel(x,y,0);
    int last_index = i->index_of_sentinel_subpixel();
    assert(index > -1 && index < last_index);

    pybuf = PyBuffer_FromReadWriteMemory(
        i->getFateBuffer()+index,
        (last_index - index)  * sizeof(fate_t));

    Py_XINCREF(pybuf);

    return pybuf;
}


static PyMethodDef PfMethods[] = {
    {"pf_load",  pf_load, METH_VARARGS, 
     "Load a new point function shared library"},
    {"pf_create", pf_create, METH_VARARGS,
     "Create a new point function"},
    {"pf_init", pf_init, METH_VARARGS,
     "Init a point function"},
    //{"pf_calc", pf_calc, METH_VARARGS, "Calculate one point"},
    //{"pf_defaults", pf_defaults, METH_VARARGS, "Get defaults for this formula"},

    //{ "cmap_create", cmap_create, METH_VARARGS, "Create a new colormap"},
    { "cmap_create_gradient", cmap_create_gradient, METH_VARARGS,
      "Create a new gradient-based colormap"},
    { "cmap_lookup", cmap_pylookup, METH_VARARGS,
      "Get a color tuple from a distance value"},
    { "cmap_lookup_flags", cmap_pylookup_with_flags, METH_VARARGS,
      "Get a color tuple from a distance value and solid/inside flags"},
    { "cmap_set_solid", pycmap_set_solid, METH_VARARGS,
      "Set the inner or outer solid color"},
    { "cmap_set_transfer", pycmap_set_transfer, METH_VARARGS,
      "Set the inner or outer transfer function"},
    
    //{ "rgb_to_hsv", pyrgb_to_hsv, METH_VARARGS, "Convert a rgb(a) list into an hsv(a) one"},
    //{ "rgb_to_hsl", pyrgb_to_hsl, METH_VARARGS, "Convert a rgb(a) list into an hls(a) one"},
    //{ "hsl_to_rgb", pyhsl_to_rgb, METH_VARARGS, "Convert an hls(a) list into an rgb(a) one"},

    { "image_create", image_create, METH_VARARGS, "Create a new image buffer"},
    { "image_resize", image_resize, METH_VARARGS, "Change image dimensions - data is deleted" },
    { "image_set_offset", image_set_offset, METH_VARARGS, "set the image tile's offset" },
    { "image_dims", image_dims, METH_VARARGS, "get a tuple containing image's dimensions"},
    { "image_clear", image_clear, METH_VARARGS, "Clear all iteration and color data from image" },

    { "image_writer_create", image_writer_create, METH_VARARGS, "create an object used to write image to disk" },

    { "image_save_header", image_save_header, METH_VARARGS, "save an image header - useful for render-to-disk"},
    { "image_save_tile", image_save_tile, METH_VARARGS, "save an image fragment ('tile') - useful for render-to-disk"},
    { "image_save_footer", image_save_footer, METH_VARARGS, "save the final footer info for an image - useful for render-to-disk"},

    { "image_read", image_read, METH_VARARGS, "read an image in from disk"},

    { "image_buffer", image_buffer, METH_VARARGS, "get the rgb data from the image"},
    { "image_fate_buffer", image_fate_buffer, METH_VARARGS, "get the fate data from the image"},

    //{ "image_get_color_index", image_get_color_index, METH_VARARGS, "Get the color index data from a point on the image"},
    //{ "image_get_fate", image_get_fate, METH_VARARGS, "Get the (solid, fate) info for a point on the image"},

    //{ "image_lookup", pyimage_lookup, METH_VARARGS, "Get the color of a point on an image"},

    //{ "site_create", pysite_create, METH_VARARGS, "Create a new site"},
    { "fdsite_create", pyfdsite_create, METH_VARARGS, "Create a new file-descriptor site"},

    // { "ff_create", ff_create, METH_VARARGS, "Create a fractFunc." },
    // { "ff_look_vector", ff_look_vector, METH_VARARGS, "Get a vector from the eye to a point on the screen" },
    // { "ff_get_vector", ff_get_vector, METH_VARARGS, "Get a vector inside the ff" },

    // { "fw_create", fw_create, METH_VARARGS, "Create a fractWorker." },
    // { "fw_pixel", fw_pixel, METH_VARARGS, "Draw a single pixel." },
    // { "fw_pixel_aa", fw_pixel_aa, METH_VARARGS, "Draw a single pixel." },
    // { "fw_find_root", fw_find_root, METH_VARARGS, "Find closest root considering fractal function along a vector"},
    
    { "calc", (PyCFunction) pycalc, METH_VARARGS | METH_KEYWORDS, "Calculate a fractal image"},

    //{ "interrupt", pystop_calc, METH_VARARGS, "Stop an async calculation" },

    // { "rot_matrix", rot_matrix, METH_VARARGS, "Return a rotated and scaled identity matrix based on params"},

    // { "eye_vector", eye_vector, METH_VARARGS, "Return the line between the user's eye and the center of the screen"},

    //{ "arena_create", pyarena_create, METH_VARARGS, "Create a new arena allocator" },
    //{ "arena_alloc", pyarena_alloc, METH_VARARGS, "Allocate a chunk of memory from the arena" },

    //{ "array_get_int", pyarray_get, METH_VARARGS, "Get an element from an array allocated in an arena" },

    //{ "array_set_int", pyarray_set, METH_VARARGS, "Set an element in an array allocated in an arena" },
    
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

    /* message type consts */
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_ITERS", ITERS);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_IMAGE", IMAGE);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_PROGRESS", PROGRESS);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_STATUS", STATUS);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_PIXEL", PIXEL);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_TOLERANCE", TOLERANCE);
    PyModule_AddIntConstant(pymod, "MESSAGE_TYPE_STATS", STATS);
}
