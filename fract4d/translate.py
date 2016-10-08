#!/usr/bin/env python

# Translate an abstract syntax tree into tree-structured intermediate
# code, performing type checking as a side effect
import sys

from absyn import *
#import fsymbol
#import ir

#from fracttypes import *

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
    def __init__(self,prefix,dump=None):
        self.sections = {}
        self.defaults = {}
        self.paramlist = {} # bookaa: { name : ParamVar }


    def default(self,node):
        for v in node.children:
            thev = NewParamVar(v)
            if thev:
                self.paramlist[thev.name] = thev


class T(TBase):
    def __init__(self,f,prefix="f", dump=None):
        TBase.__init__(self,"f",dump)
        self.basef = f

        if len(f.children) == 0:
            return

        s = f.childByName("default")
        if s: self.default(s)


class Transform(TBase):
    "For transforms (.uxf files)"
    def __init__(self,f,prefix,dump=None):
        TBase.__init__(self,prefix,dump)
        self.basef = f

        try:
            self.main(f)
            if self.dumpPreCanon:
                self.dumpSections(f,self.sections)
            self.canonicalize()
        except TranslationError, e:
            self.errors.append(e.msg)

    def main(self, f):
        if len(f.children) == 0:
            return

        if f.children[0].type == "error":
            self.error(f.children[0].leaf)
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
    def __init__(self,f,prefix,dump=None):
        TBase.__init__(self,prefix,dump)
        self.basef = f

        self.grad = []
        self.main(f)

    def main(self, f):
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
    def __init__(self,f,name,dump=None):
        TBase.__init__(self,name,dump)
        self.basef = f

        if not f.children:
            text = f.text
            from LiuD import ParseFormFile
            dict3_ = ParseFormFile.ParseFormuFile_deep(text)
            lst = dict3_['children'][0]['children']
            for dict1 in lst:
                if True:
                    m = Node1(dict1)
                else:
                    m = Node(0,0)
                    m.SerialIn(dict1)
                f.children.append(m)
            f.deepmod = dict3_['children'][0]['deepmod']

        s = f.childByName("default")
        if s: self.default(s)

