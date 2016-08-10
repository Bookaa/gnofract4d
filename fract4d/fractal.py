#!/usr/bin/env python

import string
import StringIO
import re
import os
import sys
import struct
import math
import copy
import random
from time import time as now

try:
    import fract4dcgmp as fract4dc
except ImportError, err:
    import fract4dc

# import fracttypes
import gradient
import image
import fctutils
import colorizer
import formsettings
import fc

# the version of the earliest gf4d release which can parse all the files
# this version can output
THIS_FORMAT_VERSION="3.10"

class T(fctutils.T):
    XCENTER = 0
    YCENTER = 1
    ZCENTER = 2
    WCENTER = 3
    MAGNITUDE = 4
    XYANGLE = 5
    XZANGLE = 6
    XWANGLE = 7
    YZANGLE = 8
    YWANGLE = 9
    ZWANGLE = 10

    FORMULA=0
    OUTER=1
    INNER=2
    DEFAULT_FORMULA_FILE="gf4d.frm"
    DEFAULT_FORMULA_FUNC="Mandelbrot"
    paramnames = ["x","y","z","w","size","xy","xz","xw","yz","yw","zw"]
    def __init__(self, compiler):
        fctutils.T.__init__(self)

        self.format_version = 2.8

        self.bailfunc = 0
        # formula support
        self.forms = [
            formsettings.T(compiler,self), # formula
            formsettings.T(compiler,self,"cf0"), # outer
            formsettings.T(compiler,self,"cf1") # inner
            ]

        self.transforms = []
        self.next_transform_id = 0
        self.compiler_options = { "optimize" : 1 }
        self.yflip = False
        self.periodicity = True
        self.period_tolerance = 1.0E-9
        self.auto_epsilon = False # automatically set @epsilon param, if found
        self.auto_deepen = True # automatically adjust maxiter
        self.auto_tolerance = True # automatically adjust periodicity
        self.antialias = 1
        self.compiler = compiler
        self.render_type = 0

        self.warp_param = None
        # gradient

        # default is just white outside
        self.default_gradient = gradient.Gradient()
        if False:
            self.default_gradient.segments[0].left_color = [1.0,1.0,1.0,1.0]
            self.default_gradient.segments[0].right_color = [1.0,1.0,1.0,1.0]
        else:
            self.default_gradient.load(open(self.compiler.find_file('blend.map', 3)))

        # solid colors are black
        #self.solids = [(0,0,0,255),(0,0,0,255)]

        # formula defaults
        #self.set_formula(T.DEFAULT_FORMULA_FILE,T.DEFAULT_FORMULA_FUNC,0)
        #self.set_inner("gf4d.cfrm","zero")
        #self.set_outer("gf4d.cfrm","continuous_potential")

        self.reset()

        # interaction with fract4dc library

        # colorfunc lookup
        self.colorfunc_names = [
            "default",
            "continuous_potential",
            "zero",
            "ejection_distance",
            "decomposition",
            "external_angle"]

        self.saved = True # initial params not worth saving

    def set_solid(self):
        pass

    def serialize(self,comp=False):
        out = StringIO.StringIO()
        self.save(out,False,compress=comp)
        return out.getvalue()

    def serialize_formula(self):
        out = StringIO.StringIO()
        self.save_formula(out)
        return out.getvalue()

    def deserialize(self,string):
        self.loadFctFile(StringIO.StringIO(string))

    def apply_params(self,dict):
        for (key,value) in dict.items():
            self.parseVal(key,value,None)

    def save(self,file,update_saved_flag=True,**kwds):
        print >>file, "gnofract4d parameter file"
        print >>file, "version=%s" % THIS_FORMAT_VERSION

        compress = kwds.get("compress",False)
        if compress != False:
            # compress this file
            main_file = file
            file = fctutils.Compressor()

        for pair in zip(self.paramnames,self.params):
            print >>file, "%s=%.17f" % pair

        print >>file, "maxiter=%d" % self.maxiter
        print >>file, "yflip=%s" % self.yflip
        print >>file, "periodicity=%s" % int(self.periodicity)
        print >>file, "period_tolerance=%.17f" % self.period_tolerance

        self.forms[0].save_formula_params(file,self.warp_param)
        self.forms[1].save_formula_params(file)
        self.forms[2].save_formula_params(file)

        i = 0
        for transform in self.transforms:
            transform.save_formula_params(file,None,i)
            i += 1

        print >>file, "[colors]"
        print >>file, "colorizer=1"
        #print >>file, "solids=["
        #for solid in self.solids:
        #    print >>file, "%02x%02x%02x%02x" % solid
        #print >>file, "]"
        print >>file, "[endsection]"

        if compress:
            file.close()
            print >> main_file, file.getvalue()

        if update_saved_flag:
            self.saved = True

    def save_formula(self,file):
        print >>file, "gnofract4d formula desc"
        print >>file, "version=%s" % THIS_FORMAT_VERSION

        self.forms[0].save_formula_(file)
        self.forms[1].save_formula_(file)
        self.forms[2].save_formula_(file)

        i = 0
        for transform in self.transforms:
            transform.save_formula_(file,i)
            i += 1

    def get_gradient(self):
        if self.forms[0].formula is None:
            return self.default_gradient
        g = self.forms[0].get_named_param_value("@_gradient")
        if g == 0:
            g = self.default_gradient
        return g

    def set_gradient(self, g):
        old_g = self.get_gradient()
        if old_g != g:
            self.forms[0].set_gradient(g)
            needs_redraw = False
            if self.forms[1].is_direct() or \
               self.forms[2].is_direct():
                needs_redraw = True

    def set_gradient_from_file(self, file, name):
        g = self.compiler.get_gradient(file, name)
        self.set_gradient(g)

    def parse_periodicity(self,val,f):
        try:
            self.set_periodicity(int(val))
        except ValueError:
            # might be a bool in 'True'/'False' format
            self.set_periodicity(bool(val))

    def parse_period_tolerance(self,val,f):
        self.period_tolerance = float(val)

    def set_period_tolerance(self,val):
        if val != self.period_tolerance:
            self.period_tolerance = val

    def normalize_formulafile(self,params,formindex,formtype):
        formula = params.dict.get("formula")
        if formula:
            # we have an in-line formula, use that instead of formulafile/function
            (formulafile, fname) = self.compiler.add_inline_formula(
                formula,formtype)
        else:
            formulafile = params.dict.get(
                "formulafile",self.forms[formtype].funcFile)
            fname = params.dict.get(
                "function", self.forms[formtype].funcName)
            f = self.compiler.get_parsetree(formulafile, fname)
            return (formulafile, f)

        return (formulafile, fname)

    def parse__inner_(self,val,f):
        params = fctutils.ParamBag()
        params.load(f)
        (file,func) = self.normalize_formulafile(params,2,fc.FormulaTypes.COLORFUNC)
        self.set_formula_text(func.text, 1, 2)
        # self.set_inner(file,func)
        self.forms[2].load_param_bag(params)

    def parse__outer_(self,val,f):
        params = fctutils.ParamBag()
        params.load(f)
        (file, func) = self.normalize_formulafile(params,1,fc.FormulaTypes.COLORFUNC)
        self.set_formula_text(func.text, 1, 1)
        # self.set_outer(file,func)
        self.forms[1].load_param_bag(params)

    def parse__function_(self,val,f):
        params = fctutils.ParamBag()
        params.load(f)
        (file,func) = self.normalize_formulafile(params,0,fc.FormulaTypes.FRACTAL)

        self.set_formula_text(func.text, 0, 0)
        # self.set_formula(file,func,0)

        for (name,val) in params.dict.items():
            if name == "formulafile" or name == "function" or name == "formula" or name=="":
                continue
            elif name == "a" or name =="b" or name == "c":
                # back-compat for older versions
                self.forms[0].set_named_param("@" + name, val)
            else:
                self.forms[0].set_named_item(name,val)

    def parse__transform_(self,val,f):
        which_transform = int(val)
        params = fctutils.ParamBag()
        params.load(f)
        self.set_transform_with_text(params.dict['formula'], which_transform)
        self.transforms[which_transform].load_param_bag(params)

    def reset_angles(self):
        for i in xrange(self.XYANGLE,self.ZWANGLE+1):
            self.set_param(i,0.0)

    def reset(self):
        # set global default values, then override from formula
        # set up defaults
        self.params = [
            0.0, 0.0, 0.0, 0.0, # center
            4.0, # size
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # angles
            ]

        self.bailout = 0.0
        self.maxiter = 256
        self.rot_by = math.pi/2
        self.title = self.forms[0].funcName
        self.yflip = False
        self.auto_epsilon = False
        self.period_tolerance = 1.0E-9

        self.set_formula_defaults()

    def copy_colors(self, f):
        self.set_gradient(copy.copy(f.get_gradient()))
        #self.set_solids(f.solids)

    def set_warp_param(self,param):
        if self.warp_param != param:
            self.warp_param = param

    def set_cmap(self,mapfile):
        c = colorizer.T(self)
        file = open(mapfile)
        c.parse_map_file(file)
        self.set_gradient(c.gradient)
        #self.set_solids(c.solids)

    def get_initparam(self,n,param_type):
        params = self.forms[param_type].params
        return params[n]

    def set_initparam(self,n,val, param_type):
        self.forms[param_type].set_param(n,val)

    def refresh(self):
        for i in xrange(3):
            if self.compiler.out_of_date(self.forms[i].funcFile):
                self.set_formula(
                    self.forms[i].funcFile,self.forms[i].funcName,i)

    def set_formula_defaults(self):
        if self.forms[0].formula == None:
            return

        #g = self.get_gradient()

        #self.forms[0].set_initparams_from_formula(g)

        lst = self.forms[0].formula.defaults.items()
        for (name,val) in lst:
            # FIXME helpfile,helptopic,method,precision,
            #render,skew,stretch
            if name == "maxiter":
                self.maxiter = int(val.value)
            elif name == "center" or name == "xycenter":
                self.params[self.XCENTER] = float(val.value[0].value)
                self.params[self.YCENTER] = float(val.value[1].value)
            elif name == "zwcenter":
                self.params[self.ZCENTER] = float(val.value[0].value)
                self.params[self.WCENTER] = float(val.value[1].value)
            elif name == "angle":
                self.params[self.XYANGLE] = float(val.value)
            elif name == "magn":
                self.params[self.MAGNITUDE] = float(val.value)
            elif name == "title":
                self.title = val.value
            elif name == "periodicity":
                self.periodicity=int(val.value)
            else:
                if hasattr(self,name.upper()):
                    self.params[getattr(self,name.upper())] = float(val.value)
                else:
                    print "ignored unknown parameter %s" % name

        for form in self.forms[1:] + self.transforms:
            form.reset_params()

    def set_formula(self,formulafile,func,index=0):
        self.forms[index].set_formula(formulafile,func,self.get_gradient())

        if index == 0:
            self.set_bailfunc()
            self.warp_param = None

    def set_formula_text(self, buftext, formtype, formindex):
        assert self.compiler is self.forms[formindex].compiler
        self.forms[formindex].set_formula_text_1(buftext, formtype, self.get_gradient())

        if formindex == 0:
            self.set_bailfunc()
            self.warp_param = None

    def get_saved(self):
        return self.saved

    def set_bailfunc(self):
        bailfuncs = [
            "cmag", "manhattanish","manhattanish2",
            "max2","min2",
            "real2","imag2",
            None # bailout
            ]
        funcname = bailfuncs[self.bailfunc]
        if funcname == None:
            # FIXME deal with diff
            return

        func = self.forms[0].formula.symbols.get("@bailfunc")
        if func != None:
            self.set_func(func[0],funcname,self.forms[0].formula)

    def set_func(self,func,fname,formula):
        if func.cname != fname:
            formula.symbols.set_std_func(func,fname)

    def set_periodicity(self,periodicity):
        if self.periodicity != periodicity:
            self.periodicity = periodicity

    def set_inner(self,funcfile,funcname):
        self.set_formula(funcfile,funcname,2)

    def set_outer(self,funcfile,funcname):
        self.set_formula(funcfile,funcname,1)

    def compile(self):
        if self.forms[0].formula == None:
            raise ValueError("no formula")

        desc = self.serialize_formula()

        outputfile = self.compiler.compile_all_desc(
            self.forms[0].formula,
            self.forms[1].formula,
            self.forms[2].formula,
            [x.formula for x in self.transforms],
            self.compiler_options, desc)

        return outputfile

    def all_params(self):
        p = []
        for form in self.forms:
            p += form.params
        for transform in self.transforms:
            p += transform.params
        return p

    def calc5(self, image, colormap, pfunc, xoff, yoff, xres, yres):
        #assert async == False
        #warp = self.get_warp()
        #assert warp == -1
        assert self.render_type == 0
        assert self.period_tolerance == 1.0E-9
        assert self.auto_tolerance == True
        assert self.auto_deepen == True
        assert self.periodicity == True
        #assert self.yflip == False
        assert self.antialias == 1

        #image.resize_tile(xres,yres)
        #image.set_offset(xoff,yoff)

        fract4dc.calc(
            params=self.params,
            maxiter=self.maxiter,
            pfo=pfunc,
            cmap=colormap,
            image=image._img,
            # site=site,
            xoff=xoff, yoff=yoff, xres = xres, yres = yres
            )

    def draw(self, image, outputfile):
        pfunc = fract4dc.pf_load_and_create(outputfile)

        initparams = self.all_params()
        fract4dc.pf_init(pfunc,self.params,initparams)

        # get_colormap:
        segs = self.get_gradient().segments
        colormap = fract4dc.cmap_create_gradient(segs)

        for (xoff,yoff,xres,yres) in image.get_tile_list():

            self.calc5(image, colormap, pfunc, xoff, yoff, xres, yres)

    def set_param(self,n,val):
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val

    def get_param(self,n):
        return self.params[n]

    def warn(self,msg):
        print msg

    def parse_bailfunc(self,val,f):
        # can't set function directly because formula hasn't been parsed yet
        self.bailfunc = int(val)

    def apply_colorizer(self, cf):
        if cf.read_gradient:
            self.set_gradient(cf.gradient)
        #self.set_solids(cf.solids)
        if cf.direct:
            # loading a legacy rgb colorizer
            self.set_outer("gf4d.cfrm", "rgb")

            val = "(%f,%f,%f,1.0)" % tuple(cf.rgb)
            self.forms[1].set_named_item("@col",val)

    def parse__colors_(self,val,f):
        cf = colorizer.T(self)
        cf.load(f)
        self.apply_colorizer(cf)

    def parse__colorizer_(self,val,f):
        which_cf = int(val)
        cf = colorizer.T(self)
        cf.load(f)
        if which_cf == 0:
            self.apply_colorizer(cf)
        # ignore other colorlists for now

    def parse_inner(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_inner("gf4d.cfrm",name)

    def parse_outer(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_outer("gf4d.cfrm",name)

    def set_yflip(self,yflip):
        if self.yflip != yflip:
            self.yflip = yflip

    def parse_yflip(self,val,f):
        self.yflip = (val == "1" or val == "True")

    def parse_x(self,val,f):
        self.set_param(self.XCENTER,val)

    def parse_y(self,val,f):
        self.set_param(self.YCENTER,val)

    def parse_z(self,val,f):
        self.set_param(self.ZCENTER,val)

    def parse_w(self,val,f):
        self.set_param(self.WCENTER,val)

    def parse_size(self,val,f):
        self.set_param(self.MAGNITUDE,val)

    def parse_xy(self,val,f):
        self.set_param(self.XYANGLE,val)

    def parse_xz(self,val,f):
        self.set_param(self.XZANGLE,val)

    def parse_xw(self,val,f):
        self.set_param(self.XWANGLE,val)

    def parse_yz(self,val,f):
        self.set_param(self.YZANGLE,val)

    def parse_yw(self,val,f):
        self.set_param(self.YWANGLE,val)

    def parse_zw(self,val,f):
        self.set_param(self.ZWANGLE,val)

    def parse_bailout(self,val,f):
        self.bailout = float(val)

    def parse_maxiter(self,val,f):
        self.maxiter = int(val)

    def loadFctFile(self,f):
        line = f.readline()
        if line == None or not line.startswith("gnofract4d parameter file"):
            raise Exception("Not a valid parameter file")

        self.load(f)

        self.saved = True

if __name__ == '__main__':
    g_comp = fc.Compiler()
    g_comp.add_func_path("formulas")
    g_comp.add_func_path("../formulas")
    from fc import FormulaTypes
    g_comp.add_path("../maps", FormulaTypes.GRADIENT)
    g_comp.add_path("maps", FormulaTypes.GRADIENT)
    g_comp.add_func_path(
            os.path.join(sys.exec_prefix, "share/gnofract4d/formulas"))

    f = T(g_comp)
    for arg in sys.argv[1:]:
        file = open(arg)
        f.loadFctFile(file)
        outputfile = f.compile()
        im = image.T(640,480)
        f.draw(im, outputfile)
        im.save(os.path.basename(arg) + ".png")

