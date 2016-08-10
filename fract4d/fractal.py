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
        self.outputfile = None
        self.render_type = 0
        self.pfunc = None

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
        self.dirtyFormula = True # formula needs recompiling
        self.dirty = True # parameters have changed
        self.clear_image = True

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
        self.changed()

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

            self.changed(True) #needs_redraw)

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
            self.changed(False)

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
        self.changed(False)

    def set_warp_param(self,param):
        if self.warp_param != param:
            self.warp_param = param
            self.changed(True)

    def set_cmap(self,mapfile):
        c = colorizer.T(self)
        file = open(mapfile)
        c.parse_map_file(file)
        self.set_gradient(c.gradient)
        #self.set_solids(c.solids)
        self.changed(False)

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
        self.formula_changed()
        self.changed()

    def set_formula_text(self, buftext, formtype, formindex):
        assert self.compiler is self.forms[formindex].compiler
        self.forms[formindex].set_formula_text_1(buftext, formtype, self.get_gradient())

        if formindex == 0:
            self.set_bailfunc()
            self.warp_param = None
        self.formula_changed()
        self.changed()

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

    def changed(self,clear_image=True):
        self.dirty = True
        self.saved = False
        self.clear_image = clear_image

    def formula_changed(self):
        self.dirtyFormula = True

    def set_func(self,func,fname,formula):
        if func.cname != fname:
            formula.symbols.set_std_func(func,fname)
            self.dirtyFormula = True
            self.changed()

    def set_periodicity(self,periodicity):
        if self.periodicity != periodicity:
            self.periodicity = periodicity
            self.changed()

    def set_inner(self,funcfile,funcname):
        self.set_formula(funcfile,funcname,2)

    def set_outer(self,funcfile,funcname):
        self.set_formula(funcfile,funcname,1)

    def get_transform_prefix(self):
        i = self.next_transform_id
        prefix = "t%d" % i
        self.next_transform_id += 1
        return prefix

    def append_transform(self,funcfile,funcname):
        fs = formsettings.T(self.compiler,self,self.get_transform_prefix())
        fs.set_formula(funcfile, funcname, self.get_gradient())
        self.transforms.append(fs)
        self.formula_changed()
        self.changed()

    def append_transform_(self,formula):
        fs = formsettings.T(self.compiler,self,self.get_transform_prefix())
        fs.set_formula_(formula, self.get_gradient())
        self.transforms.append(fs)
        self.formula_changed()
        self.changed()

    def set_transform(self,funcfile,funcname,i):
        fs = formsettings.T(self.compiler,self,self.get_transform_prefix())
        fs.set_formula(funcfile, funcname, self.get_gradient())
        if len(self.transforms) <= i:
            self.transforms.extend([None] * (i- len(self.transforms)+1))

        self.transforms[i] = fs
        self.formula_changed()
        self.changed()

    def set_transform_with_text(self, formulatext, i):
        fs = formsettings.T(self.compiler,self,self.get_transform_prefix())
        import translate
        type = translate.Transform
        fs.set_formula_with_text(type, formulatext, self.get_gradient())
        if len(self.transforms) <= i:
            self.transforms.extend([None] * (i- len(self.transforms)+1))

        self.transforms[i] = fs
        self.formula_changed()
        self.changed()

    def remove_transform(self,i):
        self.transforms.pop(i)
        self.formula_changed()
        self.changed()

    def set_compiler_option(self,option,val):
        self.compiler_options[option] = val
        self.dirtyFormula = True

    def apply_options(self,options):
        if options.basename and options.func:
            self.set_formula(options.basename,options.func)
            self.reset()

        if options.innername and options.innerfunc:
            self.set_inner(options.innername, options.innerfunc)
            self.reset()

        if options.outername and options.outerfunc:
            self.set_outer(options.outername, options.outerfunc)
            self.reset()

        if options.maxiter != -1:
            self.set_maxiter(options.maxiter)

        for (num,val) in options.paramchanges.items():
            self.set_param(num,val)

        for (file,func) in options.transforms:
            self.append_transform(file,func)

        if options.map:
            self.set_cmap(options.map)

        if options.antialias != None:
            self.antialias = options.antialias

    def compile(self):
        if self.forms[0].formula == None:
            raise ValueError("no formula")
        if self.dirtyFormula == False:
            return self.outputfile

        desc = self.serialize_formula()

        outputfile = self.compiler.compile_all_desc(
            self.forms[0].formula,
            self.forms[1].formula,
            self.forms[2].formula,
            [x.formula for x in self.transforms],
            self.compiler_options, desc)

        if outputfile != None:
            self.set_output_file(outputfile)

        self.dirtyFormula = False
        return self.outputfile

    def set_output_file(self, outputfile):
        if self.outputfile != outputfile:
            self.outputfile = outputfile
            self.pfunc = fract4dc.pf_load_and_create(outputfile)

    def make_random_colors(self, n):
        self.get_gradient().randomize(n)
        self.changed(False)

    def mul_vs(self,v,s):
        return map(lambda x : x * s, v)

    def xy_random(self,weirdness,size):
        return weirdness * 0.5 * size * (random.random() - 0.5)

    def zw_random(self,weirdness,size):
        factor = math.fabs(1.0 - math.log(size)) + 1.0
        return weirdness * (random.random() - 0.5 ) * 1.0 / factor

    def angle_random(self, weirdness):
        action = random.random()
        if action > weirdness:
            return 0.0 # no change

        action = random.random()
        if action < weirdness/6.0:
            # +/- pi/2
            if random.random() > 0.5:
                return math.pi/2.0
            else:
                return math.pi/2.0

        return weirdness * (random.random() - 0.5) * math.pi/2.0

    def is4D(self):
        return self.warp_param != None or self.forms[0].formula.is4D()

    def mutate(self,weirdness,color_weirdness):
        '''randomly adjust position, colors, angles and parameters.
        weirdness is between 0 and 1 - 0 is no change, 1 is lots'''

        size = self.params[self.MAGNITUDE]
        self.params[self.XCENTER] += self.xy_random(weirdness, size)
        self.params[self.YCENTER] += self.xy_random(weirdness, size)

        self.params[self.XYANGLE] += self.angle_random(weirdness)

        if self.is4D():
            self.params[self.ZCENTER] += self.zw_random(weirdness, size)
            self.params[self.WCENTER] += self.zw_random(weirdness, size)

            for a in xrange(self.XZANGLE,self.ZWANGLE):
                self.params[a] += self.angle_random(weirdness)

        if random.random() < weirdness * 0.75:
            self.params[self.MAGNITUDE] *= 1.0 + (0.5 - random.random())

        for f in self.forms:
            f.mutate(weirdness, size)

        if random.random() < color_weirdness:
            try:
                (file, formula) = self.compiler.get_random_gradient()
                self.set_gradient_from_file(file,formula)
            except IndexError:
                # can occur if no gradients available or occasionally
                # because random.choice is horked
                pass

    def nudge(self,x,y,axis=0):
        # move a little way in x or y
        self.relocate(0.025 * x , 0.025 * y, 1.0,axis)

    def get_form(self,param_type):
        if param_type > 2:
            form = self.transforms[param_type-3]
        else:
            form = self.forms[param_type]
        return form

    def nudge_param(self, i, param_type, x, y):
        form = self.get_form(param_type)
        form.nudge_param(i,x,y)

    def relocate(self,dx,dy,zoom,axis=0):
        if dx == 0 and dy == 0 and zoom == 1.0:
            return

        m = fract4dc.rot_matrix(self.params)

        deltax = self.mul_vs(m[axis],dx)
        if self.yflip:
            deltay = self.mul_vs(m[axis+1],dy)
        else:
            deltay = self.mul_vs(m[axis+1],-dy)

        self.params[self.XCENTER] += deltax[0] + deltay[0]
        self.params[self.YCENTER] += deltax[1] + deltay[1]
        self.params[self.ZCENTER] += deltax[2] + deltay[2]
        self.params[self.WCENTER] += deltax[3] + deltay[3]
        self.params[self.MAGNITUDE] *= zoom
        self.changed()

    def flip_to_julia(self):
        self.params[self.XZANGLE] += self.rot_by
        self.params[self.YWANGLE] += self.rot_by
        self.rot_by = - self.rot_by
        self.changed()

    # status callbacks
    def status_changed(self,val):
        pass

    def progress_changed(self,d):
        pass

    def stats_changed(self,s):
        pass

    def is_interrupted(self):
        return False

    def iters_changed(self,iters):
        #print "iters changed to %d" % iters
        self.maxiter = iters

    def tolerance_changed(self,tolerance):
        #print "tolerance changed to %g" % tolerance
        self.period_tolerance = tolerance

    def image_changed(self,x1,y1,x2,y2):
        pass

    def _pixel_changed(self,params,x,y,aa,maxIters,nNoPeriodIters,dist,fate,nIters,r,g,b,a):
        # remove underscore to debug fractal generation
        print "pixel: (%g,%g,%g,%g) %d %d %d %d %d %g %d %d (%d %d %d %d)" % \
              (params[0],params[1],params[2],params[3],x,y,aa,maxIters,nNoPeriodIters,dist,fate,nIters,r,g,b,a)

    def epsilon_tolerance(self,w,h):
        #5% of the size of a pixel
        return self.params[self.MAGNITUDE]/(20.0 * max(w,h))

    def all_params(self):
        p = []
        for form in self.forms:
            p += form.params
        for transform in self.transforms:
            p += transform.params
        return p

    def get_warp(self):
        if self.warp_param:
            warp = self.forms[0].order_of_name(self.warp_param)
        else:
            warp = -1
        return warp


    def calc5(self, image, colormap, xoff, yoff, xres, yres):
        #assert async == False
        #assert self.clear_image == False
        warp = self.get_warp()
        assert warp == -1
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
            pfo=self.pfunc,
            cmap=colormap,
            image=image._img,
            # site=site,
            xoff=xoff, yoff=yoff, xres = xres, yres = yres
            )

    def draw(self,image):
        initparams = self.all_params()
        fract4dc.pf_init(self.pfunc,self.params,initparams)

        # get_colormap:
        segs = self.get_gradient().segments
        colormap = fract4dc.cmap_create_gradient(segs)

        for (xoff,yoff,xres,yres) in image.get_tile_list():

            self.calc5(image, colormap, xoff, yoff, xres, yres)

    def set_param(self,n,val):
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val
            self.changed()

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
        self.changed(False)
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
            self.changed()

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

    def parse_antialias(self,val,f):
        # antialias now a user pref, not saved in file
        #self.antialias = int(val)
        pass

    def order_of_name(self,name,symbol_table):
        op = symbol_table.order_of_params()
        rn = symbol_table.mangled_name(name)
        ord = op.get(rn)
        if ord == None:
            #print "can't find %s (%s) in %s" % (name,rn,op)
            pass
        return ord

    def fix_bailout(self):
        # because bailout occurs before we know which function this is
        # in older files, we save it in self.bailout then apply to the
        # initparams later
        if self.bailout != 0.0:
            for f in self.forms:
                f.try_set_named_item("@bailout",self.bailout)

    def fix_gradients(self, old_gradient):
        # new gradient is read in after the gradient params have been set,
        # so this is needed to fix any which are using that default
        p = self.forms[0].params
        for i in xrange(len(p)):
            if p[i] == old_gradient:
                p[i] = self.get_gradient()

    def param_display_name(self,name,param):
        if hasattr(param,"title"):
            return param.title.value
        if hasattr(param,"caption"):
            return param.caption.value
        if name[:5] == "t__a_":
            name = name[5:]
        return name.title()

    def param_tip(self,name,param):
        if hasattr(param,"hint"):
            return param.hint.value
        return self.param_display_name(name,param)

    def loadFctFile(self,f):
        line = f.readline()
        if line == None or not line.startswith("gnofract4d parameter file"):
            raise Exception("Not a valid parameter file")

        self.load(f)

        self.fix_bailout()
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
        f.compile()
        im = image.T(640,480)
        f.draw(im)
        im.save(os.path.basename(arg) + ".png")

