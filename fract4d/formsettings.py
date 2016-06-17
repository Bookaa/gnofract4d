# a class to hold a formula and all the parameter settings which go with it

import copy
import math
import random
import re
import StringIO
import weakref

import fracttypes
import gradient
import image

# matches a complex number
cmplx_re = re.compile(r'\((.*?),(.*?)\)')
# matches a hypercomplex number
hyper_re = re.compile(r'\((.*?),(.*?),(.*?),(.*?)\)')

class T:
    def __init__(self,compiler,parent=None,prefix=None):
        self.compiler = compiler
        if g_useMyFormula:
            self.formule = None
        else:
            self.formula = None
        self.funcName = None
        self.funcFile = None
        self.params = []
        self.paramtypes = []
        self.dirty = False
        self.set_prefix(prefix)
        if parent:
            self.parent = weakref.ref(parent)
        else:
            self.parent = None

    def set_prefix(self,prefix):
        self.prefix = prefix
        if prefix == None:
            self.sectname = "function"
        elif prefix == "cf0":
            self.sectname = "outer"
        elif prefix == "cf1":
            self.sectname = "inner"
        elif prefix[0] == 't':
            self.sectname = "transform"
        else:
            raise ValueError("Unexpected prefix '%s' " % prefix)

    def set_initparams_from_formula(self,g):
        if g_useMyFormula:
            self.params = self.formule.symbols_default_params_()
            self.paramtypes = self.formule.symbols_type_of_params_()
        else:
            self.params = self.formula.symbols.default_params()
            self.paramtypes = self.formula.symbols.type_of_params()
        for i in xrange(len(self.paramtypes)):
            if self.paramtypes[i] == fracttypes.Gradient:
                self.params[i] = copy.copy(g)
            elif self.paramtypes[i] == fracttypes.Image:
                im = image.T(1,1)
                #b = im.image_buffer()
                #b[0] = chr(216)
                #b[3] = chr(88)
                #b[4] = chr(192)
                #b[11] = chr(255)
                self.params[i] = im

    def reset_params(self):
        if g_useMyFormula:
            self.params = self.formule.symbols_default_params_()
            self.paramtypes = self.formule.symbols_type_of_params_()
        else:
            self.params = self.formula.symbols.default_params()
            self.paramtypes = self.formula.symbols.type_of_params()

    def copy_from(self,other):
        # copy the function overrides
        for name in self.func_names():
            self.set_named_func(name,
                                other.get_func_value(name))

        # copy the params
        self.params = [copy.copy(x) for x in other.params]

    def initvalue(self,name,warp_param=None):
        ord = self.order_of_name(name)
        if g_useMyFormula:
            type = self.formule.symbols_name_type_(name)
        else:
            type = self.formula.symbols[name].type

        if type == fracttypes.Complex:
            if warp_param == name:
                return "warp"
            else:
                return "(%.17f,%.17f)"%(self.params[ord],self.params[ord+1])
        elif type == fracttypes.Hyper or type == fracttypes.Color:
            return "(%.17f,%.17f,%.17f,%.17f)"% \
                   (self.params[ord],self.params[ord+1],
                    self.params[ord+2],self.params[ord+3])
        elif type == fracttypes.Float:
            return "%.17f" % self.params[ord]
        elif type == fracttypes.Int:
            return "%d" % self.params[ord]
        elif type == fracttypes.Bool:
            return "%s" % int(self.params[ord])
        elif type == fracttypes.Gradient:
            return "[\n" + self.params[ord].serialize() + "]"
        elif type == fracttypes.Image:
            return "[\n" + self.params[ord].serialize() + "]"
        else:
            raise ValueError("Unknown type %s for param %s" % (type,name))

    def save_formula_params(self,file,warp_param=None,sectnum=None):
        if sectnum == None:
            print >>file, "[%s]" % self.sectname
        else:
            print >>file, "[%s]=%d" % (self.sectname, sectnum)

        print >>file, "formulafile=%s" % self.funcFile
        print >>file, "function=%s" % self.funcName

        if(self.compiler.is_inline(self.funcFile, self.funcName)):
            contents = self.compiler.get_formula_text(
                self.funcFile, self.funcName)
            print >>file, "formula=[\n%s\n]" % contents

        names = self.func_names()
        names.sort()
        for name in names:
            print >>file, "%s=%s" % (name, self.get_func_value(name))
        names = self.param_names()
        names.sort()
        for name in names:
            print >>file, "%s=%s" % (name, self.initvalue(name,warp_param))

        print >>file, "[endsection]"

    def save_formula_(self,file,sectnum=None):
        if sectnum == None:
            print >>file, "[%s]" % self.sectname
        else:
            print >>file, "[%s]=%d" % (self.sectname, sectnum)

        # print >>file, "formulafile=%s" % self.funcFile
        # print >>file, "function=%s" % self.funcName

        if True: # (self.compiler.is_inline(self.funcFile, self.funcName)):
            contents = self.compiler.get_formula_text(
                self.funcFile, self.funcName)
            print >>file, "formula=[\n%s\n]" % contents.strip()

        print >>file, "[endsection]"

    def func_names(self):
        if g_useMyFormula:
            return self.formule.symbols_func_names_()
        else:
            return self.formula.symbols.func_names()

    def param_names(self):
        if g_useMyFormula:
            return self.formule.symbols_param_names_()
        else:
            return self.formula.symbols.param_names()

    def params_of_type(self,type,readable=False):
        if g_useMyFormula:
            return self.formule.params_of_type_(type, readable)
        params = []
        op = self.formula.symbols.order_of_params()
        for name in op.keys():
            if name != '__SIZE__':
                if self.formula.symbols[name].type == type:
                    if readable:
                        params.append(self.formula.symbols.demangle(name))
                    else:
                        params.append(name)
        return params

    def get_func_value(self,func_to_get):
        if g_useMyFormula:
            return self.formule.get_func_value2_(func_to_get)
        fname = self.formula.symbols.demangle(func_to_get)
        func = self.formula.symbols[fname]

        return func[0].cname

    def get_named_param_value(self,name):
        if g_useMyFormula:
            op = self.formule.symbols_order_of_params_()
            from fsymbol import mangle
            ord = op.get(mangle(name))
            return self.params[ord]

        op = self.formula.symbols.order_of_params()
        ord = op.get(self.formula.symbols.mangled_name(name))
        return self.params[ord]

    def order_of_name(self,name):
        if g_useMyFormula:
            return self.formule.order_of_name_(name)
        symbol_table = self.formula.symbols
        op = symbol_table.order_of_params()
        rn = symbol_table.mangled_name(name)
        ord = op.get(rn)
        if ord == None:
            #print "can't find %s (%s) in %s" % (name,rn,op)
            pass
        return ord

    def set_gradient(self,g):
        ord = self.order_of_name("@_gradient")
        self.params[ord] = g

    def try_set_named_item(self,name,val):
        # set the item if it exists, don't worry if it doesn't
        try:
            self.set_named_item(name,val)
        except KeyError:
            pass

    def text(self):
        "Return the text of this formula"
        return self.compiler.get_formula_text(
            self.funcFile, self.funcName)

    def set_named_item(self,name,val):
        if g_useMyFormula:
            flg = self.formule.symbol_type_(name)
            if flg:
                self.set_named_func(name,val)
            else:
                self.set_named_param(name,val)
            return

        sym = self.formula.symbols[name].first()
        if isinstance(sym, fracttypes.Func):
            self.set_named_func(name,val)
        else:
            self.set_named_param(name,val)

    def set_named_param(self,name,val):
        ord = self.order_of_name(name)
        if ord == None:
            #print "Ignoring unknown param %s" % name
            return

        if g_useMyFormula:
            t = self.formule.symbols_name_type_(name)
        else:
            t = self.formula.symbols[name].type
        if t == fracttypes.Complex:
            m = cmplx_re.match(val)
            if m != None:
                re = float(m.group(1)); im = float(m.group(2))
                if self.params[ord] != re:
                    self.params[ord] = re
                    self.changed()
                if self.params[ord+1] != im:
                    self.params[ord+1] = im
                    self.changed()
            elif val == "warp":
                self.parent().set_warp_param(name)
        elif t == fracttypes.Hyper or t == fracttypes.Color:
            m = hyper_re.match(val)
            if m!= None:
                for i in xrange(4):
                    val = float(m.group(i+1))
                    if self.params[ord+i] != val:
                        self.params[ord+i] = val
                        self.changed()
        elif t == fracttypes.Float:
            newval = float(val)
            if self.params[ord] != newval:
                self.params[ord] = newval
                self.changed()
        elif t == fracttypes.Int:
            newval = int(val)
            if self.params[ord] != newval:
                self.params[ord] = newval
                self.changed()
        elif t == fracttypes.Bool:
            # don't use bool(val) - that makes "0" = True
            try:
               i = int(val)
               i = (i != 0)
            except ValueError:
               # an old release included a 'True' or 'False' string
               if val == "True": i = 1
               else: i = 0
            if self.params[ord] != i:
                self.params[ord] = i
                self.changed()
        elif t == fracttypes.Gradient:
            grad = gradient.Gradient()
            grad.load(StringIO.StringIO(val))
            self.params[ord] = grad
            self.changed()
        elif t == fracttypes.Image:
            im = image.T(2,2)
            self.params[ord] = im
            self.changed()
        else:
            raise ValueError("Unknown param type %s for %s" % (t,name))

    def set_named_func(self,func_to_set,val):
        if g_useMyFormula:
            cname = self.get_func_value(func_to_set)
            if cname == val:
                return False
            assert False
        fname = self.formula.symbols.demangle(func_to_set)
        func = self.formula.symbols.get(fname)
        return self.set_func(func[0],val)

    def zw_random(self,weirdness,size):
        factor = math.fabs(1.0 - math.log(size)) + 1.0
        return weirdness * (random.random() - 0.5 ) * 1.0 / factor

    def mutate(self, weirdness, size):
        for i in xrange(len(self.params)):
            if self.paramtypes[i] == fracttypes.Float:
                self.params[i] += self.zw_random(weirdness, size)
            elif self.paramtypes[i] == fracttypes.Int:
                # FIXME: need to be able to look up enum to find min/max
                pass
            elif self.paramtypes[i] == fracttypes.Bool:
                if random.random() < weirdness * 0.2:
                    self.params[i] = not self.params[i]

    def nudge_param(self,n,x,y):
        if x == 0 and y == 0:
            return False

        self.params[n] += (0.025 * x)
        self.params[n+1] += (0.025 * y)
        self.changed()
        return True

    def set_param(self,n,val):
        # set the N'th param to val, after converting from a string
        t = self.paramtypes[n]

        if t == fracttypes.Float:
            val = float(val)
        elif t == fracttypes.Int:
            val = int(val)
        elif t == fracttypes.Bool:
            val = bool(val)
        else:
            raise ValueError("Unknown parameter type %s" % t)

        if self.params[n] != val:
            self.params[n] = val
            self.changed()
            return True
        return False

    def set_func(self,func,fname):
        if func.cname != fname:
            self.formula.symbols.set_std_func(func,fname)
            self.dirty = True
            self.changed()
            return True
        else:
            return False

    def changed(self):
        self.dirty = True
        if self.parent:
            self.parent().changed()

    def is_direct(self):
        return self.formula.is_direct()

    def set_formula(self,file,func,gradient):
        if '__inline__' in file:
            pass
        if g_useMyFormula:
            sbody = ''
            if '__inline__' in file:
                import os
                basefile = os.path.basename(file)
                assert basefile in self.compiler.files
                sbody = self.compiler.files[basefile].contents

            formula = MyFormula(file, func, self.prefix, sbody, self.compiler)
            self.formule = formula
        else:
            formula = self.compiler.get_formula(file,func,self.prefix)

            if formula == None:
                raise ValueError("no such formula: %s:%s" % (file, func))

            if formula.errors != []:
                raise ValueError("invalid formula '%s':\n%s" % \
                                 (func, "\n".join(formula.errors)))

            self.formula = formula
        self.funcName = func
        self.funcFile = file

        self.set_initparams_from_formula(gradient)

    def load_param_bag(self,bag):
        for (name,val) in bag.dict.items():
            if name == "formulafile" or name=="function":
                pass
            else:
                self.try_set_named_item(name,val)

    def blend(self, other, ratio):
        # update in-place our settings so that they are a mixture with the other
        if self.funcName != other.funcName or self.funcFile != other.funcFile:
            raise ValueError("Cannot blend parameters between different formulas")

        for i in xrange(len(self.params)):
            (a,b) = (self.params[i],other.params[i])
            if self.paramtypes[i] == fracttypes.Float:
                self.params[i] = a*(1.0-ratio) + b*ratio
            elif self.paramtypes[i] == fracttypes.Int:
                self.params[i] = int(a*(1.0-ratio) + b*ratio)
            elif self.paramtypes[i] == fracttypes.Bool:
                if ratio >= 0.5:
                    self.params[i] = b
            else:
                # don't interpolate
                pass

g_useMyFormula = True

class MyFormula:
    def __init__(self, file_, func_, prefix_, sbody, compiler):
        if True:
            self.file_ = file_
            self.func_ = func_
            self.prefix_ = prefix_
            self.sbody = sbody
            self.dict_ = Call_subprocess_2(file_, func_, prefix_, sbody)
            import fsymbol
            self.default_dict = fsymbol.createDefaultDict()
            self.me = None
        else:
            self.me = compiler.get_formula(file_,func_,prefix_)


        #  formula = self.compiler.get_formula(self.file_, self.func_, self.prefix_)
        # self.compiler is fract4d.fc.Compiler

        #self.params = self.formula.symbols.default_params()
        #self.paramtypes = self.formula.symbols.type_of_params()
    def symbols_default_params_(self):
        if self.me:
            return self.me.symbols.default_params()
        return self.dict_['params']
    def symbols_type_of_params_(self):
        if self.me:
            return self.me.symbols.type_of_params()
        return self.dict_['paramtypes']
    def defaults_items_(self):
        if self.me:
            return self.me.defaults.items()
        return self.dict_['defaults_items']
    def symbols_func_names_(self):
        if self.me:
            return self.me.symbols.func_names()
        return self.dict_['symbols_func_names']
    def symbols_param_names_(self):
        if self.me:
            return self.me.symbols.param_names()
        return self.dict_['symbols_param_names']

    def symbols_order_of_params_(self):
        if self.me:
            return self.me.symbols.order_of_params()
        return self.dict_['op']

    def get_func_value_(self, func_to_get):
        if self.me:
            func = self.me.symbols.get(func_to_get)
            if func is None:
                return None
            return func[0].cname

        fname = demangle(func_to_get)
        cnames = self.dict_['cnames']
        cname = cnames.get(fname)
        if cname:
            return cname
        import fsymbol
        fname2 = fsymbol.mangle(fname)
        cname = cnames.get(fname2)
        if cname:
            return cname

        return None

    def get_func_value2_(self, func_to_get):
        if self.me:
            fname = self.me.symbols.demangle(func_to_get)
            func = self.me.symbols[fname]
            return func[0].cname
        fname = demangle(func_to_get)
        cnames = self.dict_['cnames']
        cname = cnames.get(fname)
        if cname:
            return cname
        import fsymbol
        fname2 = fsymbol.mangle(fname)
        cname = cnames.get(fname2)
        if cname:
            return cname

        assert False

    def order_of_name_(self,name):
        if self.me:
            symbol_table = self.me.symbols
            op = symbol_table.order_of_params()
            rn = symbol_table.mangled_name(name)
            ord = op.get(rn)
            if ord == None:
                #print "can't find %s (%s) in %s" % (name,rn,op)
                pass
            return ord

        import fsymbol
        rn = fsymbol.mangle(name)
        op = self.dict_['op']
        ord = op.get(rn)
        if ord is not None:
            return ord
        assert False
        symbol_table = self.formula.symbols
        op = symbol_table.order_of_params()
        # rn = symbol_table.mangled_name(name)
        ord = op.get(rn)
        if ord == None:
            #print "can't find %s (%s) in %s" % (name,rn,op)
            pass
        return ord
    def symbols_name_type_(self, name):
        if self.me:
            return self.me.symbols[name].type
        fname = demangle(name)
        types = self.dict_['types']
        type1 = types.get(fname)
        if type1:
            return type1
        import fsymbol
        fname2 = fsymbol.mangle(fname)
        type1 = types.get(fname2)
        if type1:
            return type1
        assert False

    def params_of_type_(self, type, readable):
        if self.me:
            params = []
            op = self.me.symbols.order_of_params()
            for name in op.keys():
                if name != '__SIZE__':
                    if self.me.symbols[name].type == type:
                        if readable:
                            params.append(self.me.symbols.demangle(name))
                        else:
                            params.append(name)
            return params

        params = []
        op = self.dict_['op']
        for name in op.keys():
            if name != '__SIZE__':
                if self.symbols_name_type_(name) == type:
                    if readable:
                        params.append(demangle(name))
                    else:
                        params.append(name)
        return params

    def symbols_parameters_(self):
        if self.me:
            return self.me.symbols.parameters()
        d1 = self.dict_['dict_params']
        d2 = {}
        for key, value in d1.items():
            if value.keys() == ['Var']:
                typ_,value_,pos_ = value.values()[0]
                vnew = fracttypes.Var(typ_,value_,pos_)
                d2[key] = vnew
            elif value.keys() == ['Func']:
                args_, implicit_args, ret_, pos_, fname_ = value.values()[0]
                fnew = fracttypes.Func(args_,ret_,fname_,pos_)
                fnew.implicit_args = implicit_args
                d2[key] = fnew
            else:
                assert False
        return d2

    def available_param_functions_(self,ret,args):
        if self.me:
            return self.me.symbols.available_param_functions(ret, args)
        # a list of all function names which take args of type 'args'
        # and return 'ret' (for GUI to select a function)
        def _is_private(key):
            return key[0:3] == "t__"
        flist = []
        for (name,func) in self.default_dict.items():
            try:
                for f in func:
                    if f.ret == ret and f.args == args and \
                           not _is_private(name) and \
                           not func.is_operator():
                        flist.append(name)
            except TypeError:
                # wasn't a list
                pass

        return flist

    def is4D_(self):
        if self.me:
            return self.me.is4D()
        return self.dict_['is4D']

    def symbol_type_(self, name):
        if self.me:
            sym = self.me.symbols[name].first()
            return isinstance(sym, fracttypes.Func)

        types = self.dict_['dict4']
        fname = demangle(name)
        type1 = types.get(fname)
        if type1 is not None:
            return type1
        import fsymbol
        fname2 = fsymbol.mangle(fname)
        type1 = types.get(fname2)
        if type1 is not None:
            return type1
        assert False

def fn33(params):
    for key, param in params.items():
        if isinstance(param, fracttypes.Var):
            print key, 'Var(%s,%s,%s)' % (param.type, param.value, param.pos)
        elif isinstance(param, fracttypes.Func):
            print key, 'Func', (param.args, param.implicit_args, param.ret, param.pos, param.fname)
        else:
            assert False


def Call_subprocess_2(file_, func_, prefix_, sbody):
    import json
    from subprocess import PIPE, Popen
    p = Popen(["python", '../gnofract4d.compiler/main_compile.py'], stdin=PIPE, stdout=PIPE)
    if sbody:
        print >>p.stdin, '3'
        s3 = json.dumps(sbody)
        print >>p.stdin, s3
    else:
        print >>p.stdin, '2'
    print >>p.stdin, file_
    print >>p.stdin, func_
    print >>p.stdin, prefix_
    while True:
        s = p.stdout.readline().strip()
        if s == 'next is json':
            break
        print s
    sJson = p.communicate("\n")[0]
    dict_ = json.loads(sJson)
    # print 'i get', dict_
    return dict_

def demangle(name):
    # remove most obvious mangling.
    # because of case-folding, demangle(mangle(s)) != s
    if name[:3] == "t__":
        name = name[3:]

    if name[:2] == "a_":
        name = "@" + name[2:]
    elif name[:2] == "h_":
        name = "#" + name[2:]

    return name
