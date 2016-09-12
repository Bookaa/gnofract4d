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

import myfract4dc

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
        self.compiler = compiler

        # default is just white outside
        self.default_gradient = gradient.Gradient()
        self.default_gradient.segments[0].left_color = [1.0,1.0,1.0,1.0]
        self.default_gradient.segments[0].right_color = [1.0,1.0,1.0,1.0]

        # set global default values, then override from formula
        # set up defaults
        self.params = [ 0.0, 0.0, 0.0, 0.0, # center
                        4.0, # size
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0 # angles
                      ]

        self.bailout = 0.0
        self.maxiter = 256
        self.rot_by = math.pi/2
        self.title = self.forms[0].funcName

        self.colorfunc_names = [
            "default",
            "continuous_potential",
            "zero",
            "ejection_distance",
            "decomposition",
            "external_angle"]

    def serialize_formula(self):
        out = StringIO.StringIO()
        self.save_formula(out)
        return out.getvalue()

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
        self.forms[2].load_param_bag(params)

    def parse__outer_(self,val,f):
        params = fctutils.ParamBag()
        params.load(f)
        (file, func) = self.normalize_formulafile(params,1,fc.FormulaTypes.COLORFUNC)
        self.set_formula_text(func.text, 1, 1)
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

    def set_formula(self,formulafile,func,index=0):
        self.forms[index].set_formula(formulafile,func,self.get_gradient())

        if index == 0:
            self.set_bailfunc()

    def set_formula_text(self, buftext, formtype, formindex):
        assert self.compiler is self.forms[formindex].compiler
        self.forms[formindex].set_formula_text_1(buftext, formtype, self.get_gradient())

        if formindex == 0:
            self.set_bailfunc()

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

    def compile(self):
        assert False

    def all_params(self):
        p = []
        for form in self.forms:
            n2 = 0
            for varr in form.formula.symbols.var_params:
                typ = varr.type
                if typ == 3:    # complex
                    p.append(((form.params[n2], form.params[n2+1]), varr))
                    n2 += 1
                else:
                    p.append((form.params[n2], varr))
                n2 += 1
            #p1 = zip(form.params, form.paramtypes, form.formula.symbols.var_params)
            # p += form.params
            #p += p1
        for transform in self.transforms:
            assert False    # alert me
            p += transform.params
        return p

    def draw(self, image, outputfile):
        formuName = self.forms[0].funcName
        initparams = self.all_params()
        segs = self.get_gradient().segments

        form0_mod = self.forms[0].formula.basef.deepmod
        form1_mod = self.forms[1].formula.basef.deepmod
        form2_mod = self.forms[2].formula.basef.deepmod
        form0_text = self.forms[0].formula.basef.text; form0_leaf = self.forms[0].formula.basef.leaf
        form1_text = self.forms[1].formula.basef.text; form1_leaf = self.forms[1].formula.basef.leaf   # continuous_potential
        form2_text = self.forms[2].formula.basef.text; form2_leaf = self.forms[2].formula.basef.leaf   # Angel
        # myfract4dc.CompileLLVM(form0_text, form0_leaf, form1_text, form1_leaf, form2_text, form2_leaf)
        myfract4dc.CompileLLVM(form0_mod, form1_mod, form2_mod)
        myfract4dc.draw(image, outputfile, formuName, initparams, self.params, segs, self.maxiter)
        return

    def set_param(self,n,val):
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val

    def parse_bailfunc(self,val,f):
        # can't set function directly because formula hasn't been parsed yet
        self.bailfunc = int(val)

    def parse__colors_(self,val,f):
        cf = colorizer.T(self)
        cf.load(f)
        # apply_colorizer :
        if cf.read_gradient:
            self.set_gradient(cf.gradient)

    def parse__colorizer_(self,val,f):
        which_cf = int(val)
        cf = colorizer.T(self)
        cf.load(f)
        if which_cf == 0:
            self.apply_colorizer(cf)
        # ignore other colorlists for now

    def parse_inner(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_formula("gf4d.cfrm", name, 2)

    def parse_outer(self,val,f):
        name = self.colorfunc_names[int(val)]
        self.set_formula("gf4d.cfrm", name, 1)

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
        outputfile = None # f.compile()
        im = image.T(640,480)
        from datetime import datetime
        t1 = datetime.now()
        f.draw(im, outputfile)
        t2 = datetime.now()
        delta = t2 - t1
        print 'time last :', delta.seconds, delta
        im.save(os.path.basename(arg) + ".png")

