#!/usr/bin/env python

# Translate an abstract syntax tree into tree-structured intermediate
# code, performing type checking as a side effect
import sys

from absyn import *
#import fsymbol
#import ir

#from fracttypes import *
import fractal

allowed_param_names = [
    "default",
    "caption",
    "min",
    "max",
    "enum",
    "hint"
]

class ParamVar:
    pass

def NewParamVar(v):
    pass
    # return ParamVar()
    the = ParamVar()
    the.name = v.leaf
    the.type = v.type # maybe 'param
    the.datatype = v.datatype
    the.value = 0
    the.enum = None

    if the.name == 'colortype':
        pass

    for v1 in v.children:
        if v1.type == 'set':
            if v1.children[0].leaf == 'enum':
                c1 = v1.children[1]
                lst3 = [c1.leaf]
                for v in c1.children:
                    lst3.append(v.leaf)
                the.enum = lst3
                continue
            if v1.children[0].leaf == 'default':
                c1 = v1.children[1]
                if the.type == 'func':
                    the.value = c1.leaf
                    continue
                if c1.type == 'const':
                    val = c1.leaf
                    the.value = val
                elif c1.type == 'id':
                    val = c1.leaf
                    the.value = val
                elif c1.type == 'string':
                    the.value = c1.leaf
                elif c1.type == 'funcall':
                    if v.datatype == 4 and c1.leaf == 'rgb':
                        the.value = (c1.children[0].leaf, c1.children[1].leaf, c1.children[2].leaf, 1.0)
                    else:
                        assert False
                elif c1.leaf == 'complex' and the.datatype == 3 and c1.type == 'binop':
                    the.value = (c1.children[0].leaf, c1.children[1].leaf)
                else:
                    assert False
    if the.datatype is None: # why not datatype
        if isinstance(the.value, float):
            the.datatype = 2 # float
        elif the.enum:
            the.datatype = 1 # int
        else:
            assert False

    if the.enum and isinstance(the.value, str):
        the.value = the.enum.index(the.value)

    return the

class TBase:
    def __init__(self):
        self.paramlist1 = {} # bookaa: { name : ParamVar }


    def default(self,node):
        for v in node.children:
            thev = NewParamVar(v)
            if thev:
                self.paramlist1[thev.name] = thev

    def GetDefaultValues(self):
        dict_ = {}
        for name, var in self.paramlist1.items():
            dict_[name] = (var.datatype, var.type, var.value, var.enum)
        dict2 = fractal.GetDefaultVals(self.mod)
        flg = dict_ == dict2
        if not flg:
            keys1 = dict_.keys()
            keys2 = dict2.keys()
            if set(keys1) != set(keys2):
                assert False
            for name in keys1:
                val1 = dict_[name]
                val2 = dict2[name]
                if val1 != val2:
                    assert False
        return dict_


class T(TBase):
    def __init__(self, f, mod):
        TBase.__init__(self)
        self.basef = f
        self.mod = mod

        if len(f.children) == 0:
            return

        s = f.childByName("default")
        if s: self.default(s)


class Transform(TBase):
    "For transforms (.uxf files)"
    def __init__(self, f, mod):
        TBase.__init__(self)
        self.basef = f
        self.mod = mod

        if len(f.children) == 0:
            return

        s = f.childByName("default")
        if s: self.default(s)
        s = f.childByName("global")
        if s: self.global_(s)
        s = f.childByName("transform")
        if s: self.transform(s)

    def transform(self,node):
        self.add_to_section("transform", self.stmlist(node))

class GradientFunc(TBase):
    "For translating UltraFractal .ugr files"
    def __init__(self, f, mod):
        TBase.__init__(self)
        self.basef = f
        self.mod = mod

        self.grad = []

        if len(f.children) == 0:
            return

        if f.children[0].type == "error":
            self.error(f.children[0].leaf)
            return

        # lookup sections in order
        s = f.childByName("gradient")
        if s: self.gradient(s)
        s = f.childByName("opacity")
        if s: self.opacity(s)

    def gradient(self, node):
        self.update_settings("gradient", node)

    def opacity(self, node):
        self.update_settings("opacity", node)

    def set(self,node):
        name = node.children[0].leaf
        val = self.const_exp(node.children[1])
        return ir.Move(
            ir.Var(name, node, val.datatype),
            val, node, val.datatype)

class ColorFunc(TBase):
    "For translating .ucl files"
    def __init__(self, f, mod):
        TBase.__init__(self)
        self.basef = f
        self.mod = mod

        s = f.childByName("default")
        if s: self.default(s)

