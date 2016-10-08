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
#import fctutils
import colorizer
import formsettings
import fc

# the version of the earliest gf4d release which can parse all the files
# this version can output
THIS_FORMAT_VERSION="3.10"

class T:
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
        self.format_version = 2.8

        self.bailfunc = 0
        # formula support
        self.forms = [
            formsettings.T(compiler), # formula
            formsettings.T(compiler,"cf0"), # outer
            formsettings.T(compiler,"cf1") # inner
            ]

        self.transforms = []
        self.next_transform_id = 0
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
        self.periodicity = True
        self.period_tolerance = 1.0E-9

        self.colorfunc_names = [
            "default",
            "continuous_potential",
            "zero",
            "ejection_distance",
            "decomposition",
            "external_angle"]

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
            self.periodicity = bool(int(val))
        except ValueError:
            # might be a bool in 'True'/'False' format
            self.periodicity = bool(val)

    def parse_period_tolerance(self,val,f):
        self.period_tolerance = float(val)

    def parse__inner_1(self, vlst):
        self.forms[2].deeplist = vlst
        params_dict = {}
        for v in vlst:
            if isinstance(v, Ast_GFF.GFF_fctfs_formula):
                assert isinstance(v.v, Ast_GFF.GFF_formu)
                v = v.v
                assert v.vq is None
                s = v.n + '{\n' + '\n'.join([v1.n for v1 in v.vlst]) + '\n}'
                self.set_formula_text(s, 1, 2)
                continue
            if isinstance(v, Ast_GFF.GFF_NameEquValue2):
                assert isinstance(v.v1, Ast_GFF.GFF_Name2)
                name = '@'+v.v1.n
                val = ValueToString(v.v2)
                #self.forms[2].set_named_item(name,val)
                self.forms[2].paramlist2[v.v1.n] = val
                continue
            if isinstance(v, Ast_GFF.GFF_gradient):
                name = '@_gradient'
                val = '\n'.join([v1.n for v1 in v.vlst])
                #self.forms[2].set_named_item(name,val)
                self.forms[2].paramlist2['_gradient'] = val
                continue
            if isinstance(v, Ast_GFF.GFF_ExtEqu):
                name = v.s
                val = v.n
                if name in ('formulafile', 'function'):
                    params_dict[name] = val
                    if len(params_dict) == 2: # we have both
                        formtype = 2
                        formulafile = params_dict.get("formulafile")
                        fname = params_dict.get("function")
                        f = self.compiler.get_parsetree(formulafile, fname)
                        #self.set_formula_text(f.text, 1, 2)
                        self.set_formula_text(f, 1, 2)
                    continue
                assert False


            assert False

    def parse__outer_1(self, vlst):
        self.forms[1].deeplist = vlst
        params_dict = {}
        for v in vlst:
            if isinstance(v, Ast_GFF.GFF_fctfs_formula):
                assert isinstance(v.v, Ast_GFF.GFF_formu)
                v = v.v
                assert v.vq is None
                s = v.n + '{\n' + '\n'.join([v1.n for v1 in v.vlst]) + '\n}'
                self.set_formula_text(s, 1, 1)
                continue
            if isinstance(v, Ast_GFF.GFF_NameEquValue2):
                assert isinstance(v.v1, Ast_GFF.GFF_Name2)
                name = '@'+v.v1.n
                if isinstance(v.v2, Ast_GFF.GFF_Name0):
                    val = v.v2.n
                elif isinstance(v.v2, Ast_GFF.GFF_Number):
                    val = v.v2.f
                else:
                    assert False
                #self.forms[1].set_named_item(name,val)
                self.forms[1].paramlist2[v.v1.n] = val
                continue
            if isinstance(v, Ast_GFF.GFF_gradient):
                name = '@_gradient'
                val = '\n'.join([v1.n for v1 in v.vlst])
                #self.forms[1].set_named_item(name,val)
                self.forms[1].paramlist2['_gradient'] = val
                continue
            if isinstance(v, Ast_GFF.GFF_ExtEqu):
                name = v.s
                val = v.n
                if name in ('formulafile', 'function'):
                    params_dict[name] = val
                    if len(params_dict) == 2: # we have both
                        formtype = 1
                        formulafile = params_dict.get("formulafile")
                        fname = params_dict.get("function")
                        f = self.compiler.get_parsetree(formulafile, fname)
                        #self.set_formula_text(f.text, 1, 1)
                        self.set_formula_text(f, 1, 1)
                    continue
                assert False

            assert False

    def parse__function_1(self, vlst):
        self.forms[0].deeplist = vlst
        params_dict = {}
        for v in vlst:
            if isinstance(v, Ast_GFF.GFF_fctfs_formula):
                assert isinstance(v.v, Ast_GFF.GFF_formu)
                v = v.v
                assert v.vq is None
                s = v.n + '{\n' + '\n'.join([v1.n for v1 in v.vlst]) + '\n}'
                self.set_formula_text(s, 0, 0)
                continue
            if isinstance(v, Ast_GFF.GFF_NameEquValue):
                assert isinstance(v.v1, Ast_GFF.GFF_Name0)
                name = v.v1.n
                val = ValueToString(v.v2)
                #self.forms[0].set_named_item(name,val)
                continue
            if isinstance(v, Ast_GFF.GFF_NameEquValue2):
                assert isinstance(v.v1, Ast_GFF.GFF_Name2)
                name = '@'+v.v1.n
                val = ValueToString(v.v2)
                #self.forms[0].set_named_item(name,val)
                self.forms[0].paramlist2[v.v1.n] = val
                continue
            if isinstance(v, Ast_GFF.GFF_gradient):
                name = '@_gradient'
                val = '\n'.join([v1.n for v1 in v.vlst])
                #self.forms[0].set_named_item(name,val)
                self.forms[0].paramlist2['_gradient'] = val
                continue
            if isinstance(v, Ast_GFF.GFF_ExtEqu):
                name = v.s
                val = v.n
                if name in ('formulafile', 'function'):
                    params_dict[name] = val
                    if len(params_dict) == 2: # we have both
                        formtype = 0
                        formulafile = params_dict.get("formulafile")
                        fname = params_dict.get("function")
                        f = self.compiler.get_parsetree(formulafile, fname)
                        #self.set_formula_text(f.text, 0, 0)
                        self.set_formula_text(f, 0, 0)
                    continue
                assert False

            assert False


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
        self.forms[formindex].set_formula_text_1(buftext, formtype, None) #self.get_gradient())

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

        #func = self.forms[0].formula.symbols.get("@bailfunc")
        #if func != None:
        #    self.set_func(func[0],funcname,self.forms[0].formula)

    def set_func(self,func,fname,formula):
        if func.cname != fname:
            formula.symbols.set_std_func(func,fname)

    def compile(self):
        assert False

    def draw(self, image, outputfile):

        if True:
            formuName = ''
            initparams = None

            form0_mod = self.forms[0].formula.basef.deepmod
            form1_mod = self.forms[1].formula.basef.deepmod
            form2_mod = self.forms[2].formula.basef.deepmod

            param0 = self.bookaa_GetParam(self.forms[0], 0)
            param1 = self.bookaa_GetParam(self.forms[1], 1)
            param2 = self.bookaa_GetParam(self.forms[2], 2)

            myfract4dc.CompileLLVM(form0_mod, form1_mod, form2_mod, param0, param1, param2)

            gradient1 = self.bookaa_GetGradient(self.forms[0])
            segs = gradient1.segments
        cmap = myfract4dc.cmap_from_pyobject(segs)
        myfract4dc.draw(image, outputfile, formuName, initparams, self.params, cmap,
                        self.maxiter, self.periodicity, self.period_tolerance)
        return

    def bookaa_GetGradient(self, theform):
        s = theform.paramlist2.get('_gradient')
        if s:
            if isinstance(s, str):
                the = gradient.Gradient()
                the.load(StringIO.StringIO(s))
                return the
            return s
        return self.default_gradient

    def bookaa_GetParam(self, theform, no):
        dict_ = theform.formula.GetDefaultValues()

        if no != 0:
            if '_density' not in dict_:
                dict_['_density'] = (2, 'param', 1.0, None)
            if '_offset' not in dict_:
                dict_['_offset'] = (2, 'param', 0.0, None)

        for name, s in theform.paramlist2.items():
            if name in dict_:
                (typ1, typ2, val, enum) = dict_[name]
                if typ2 == 'func':
                    dict_[name] = (typ1, typ2, s, enum)
                elif typ2 == 'param':
                    if typ1 == 2: # double
                        val2 = float(s)
                        dict_[name] = (typ1, typ2, val2, enum)
                    elif typ1 == 1: # int
                        val2 = int(s)
                        dict_[name] = (typ1, typ2, val2, enum)
                    elif typ1 == 3: # complex
                        dict_[name] = (typ1, typ2, val, enum)
                    else:
                        assert False
                else:
                    assert False
            elif name == '_transfer':
                dict_[name] = (97, 'param', s, None)
            elif name == '_gradient':
                continue
            else:
                assert False
        lst2 = []
        for name in dict_:
            if name == 'xpos':
                pass
            (typ1, typ2, val, enum) = dict_[name]
            if typ2 == 'func':
                lst2.append((name, 98, val, enum))
                continue
            if typ2 == 'param':
                lst2.append((name, typ1, val, enum))
                continue
            assert False

        return lst2

    def set_param(self,n,val):
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val

    def parse_bailfunc(self,val,f):
        # can't set function directly because formula hasn't been parsed yet
        self.bailfunc = int(val)

    def parse__colors_1(self,vlst):
        self.color_deeplist = vlst
        cf = colorizer.T(self)
        cf.load_1(vlst)
        if cf.read_gradient:
            #self.set_gradient(cf.gradient)
            self.forms[0].paramlist2['_gradient'] = cf.gradient

    def parse_inner(self,val,f):
        name = self.colorfunc_names[int(val)]
        # self.set_formula("gf4d.cfrm", name, 2)
        f = self.compiler.get_parsetree("gf4d.cfrm", name)
        #self.set_formula_text(f.text, 1, 2)
        self.set_formula_text(f, 1, 2)

    def parse_outer(self,val,f):
        name = self.colorfunc_names[int(val)]
        #self.set_formula("gf4d.cfrm", name, 1)
        f = self.compiler.get_parsetree("gf4d.cfrm", name)
        #self.set_formula_text(f.text, 1, 1)
        self.set_formula_text(f, 1, 1)

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

def ValueToString(v):
    if isinstance(v, Ast_GFF.GFF_Name0):
        val = v.n
    elif isinstance(v, Ast_GFF.GFF_Number):
        val = v.f
    elif isinstance(v, Ast_GFF.GFF_Numi):
        val = str(v.i)
    elif isinstance(v, Ast_GFF.GFF_Num_Complex):
        val = '(%s,%s)' % (ValueToString(v.v1), ValueToString(v.v2))
    else:
        assert False
    return val

from LiuD import Ast_GFF
class MyLoadFCT(Ast_GFF.GFF_sample_visitor_01):
    def __init__(self, f):
        self.f = f
    def visit_NameEquValue(self, node):
        name = node.v1.walkabout(self)
        value = node.v2.walkabout(self)
        if name in ('version', 'yflip', 'antialias'):
            return # ignore
        if name == 'x':  return self.f.parse_x(value, None)
        if name == 'y':  return self.f.parse_y(value, None)
        if name == 'z':  return self.f.parse_z(value, None)
        if name == 'w':  return self.f.parse_w(value, None)
        if name == 'size':  return self.f.parse_size(value, None)
        if name == 'xy':  return self.f.parse_xy(value, None)
        if name == 'xz':  return self.f.parse_xz(value, None)
        if name == 'xw':  return self.f.parse_xw(value, None)
        if name == 'yz':  return self.f.parse_yz(value, None)
        if name == 'yw':  return self.f.parse_yw(value, None)
        if name == 'zw':  return self.f.parse_zw(value, None)
        if name == 'bailout':  return self.f.parse_bailout(value, None)
        if name == 'maxiter':  return self.f.parse_maxiter(value, None)
        if name == 'bailfunc': return self.f.parse_bailfunc(value, None)
        if name == 'inner': return self.f.parse_inner(value, None)
        if name == 'outer': return self.f.parse_outer(value, None)
        if name == 'periodicity': return self.f.parse_periodicity(value, None)
        if name == 'period_tolerance': return self.f.parse_period_tolerance(value, None)
        assert False
    def visit_fctf_section(self, node):
        sec_name = node.n
        if sec_name == 'function':
            self.f.parse__function_1(node.vlst)
        elif sec_name == 'outer':
            self.f.parse__outer_1(node.vlst)
        elif sec_name == 'inner':
            self.f.parse__inner_1(node.vlst)
        elif sec_name == 'colors':
            self.f.parse__colors_1(node.vlst)
        else:
            assert False
    def visit_Name0(self, node):
        return node.n
    def visit_Number(self, node):
        return node.f
    def visit_Numi(self, node):
        return str(node.i)
def MyloadFctFile(file, f):
    if False:
        f.loadFctFile(file)
    srctxt = file.read()
    pass
    parser = Ast_GFF.Parser(srctxt)
    mod = parser.handle_FCT_File()
    if mod is None:
        lastpos, lastlineno, lastcolumn, lastline = parser.GetLast()
        print 'parse error, last pos = %d' % lastpos
        print 'last lineno = %d, column = %d' % (lastlineno, lastcolumn)
        print 'last line :', lastline
    else:
        print 'parse success'
    the = MyLoadFCT(f)
    mod.walkabout(the)

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
        if False:
            f.loadFctFile(file)
        else:
            MyloadFctFile(file, f)
        outputfile = None # f.compile()
        im = image.T(1024,768)
        #im = image.T(320,200)
        from datetime import datetime
        t1 = datetime.now()
        f.draw(im, outputfile)
        t2 = datetime.now()
        delta = t2 - t1
        print 'time last :', delta.seconds, delta
        im.save(os.path.basename(arg) + ".png")

