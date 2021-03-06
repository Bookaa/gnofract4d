# fract compiler datatypes

import string
import exceptions
import types
import copy

# order is significant - we use X > Y on types
Bool = 0
Int = 1
Float = 2
Complex = 3
Color = 4
String = 5
Hyper = 6
Gradient = 7
Image = 8

VoidArray = 9
IntArray = 10
FloatArray = 11
ComplexArray = 12

class Type(object):
    def __init__(self,**kwds):
        self.suffix = kwds["suffix"]
        self.printf = kwds.get("printf") # optional
        self.typename = kwds["typename"]
        self.default = kwds["default"]
        self.slots = kwds.get("slots",1)
        self.cname = kwds["cname"]
        self.typeid = kwds["id"]
        self.part_names = kwds.get("parts",[""])

    def init_val(self,var):
        return "0"
    
class FloatType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            return ["%.17f" % var.value]
        else:
            return ["t__pfo->p[%d].doubleval" % var.param_slot]

class ComplexType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            return [
                "%.17f" % var.value[0],
                "%.17f" % var.value[1]]     
        else:
            return [
                "t__pfo->p[%d].doubleval" % var.param_slot,
                "t__pfo->p[%d].doubleval" % (var.param_slot+1)]

class QuadType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            return [ "%.17f" % x for x in var.value]
        else:
            return [
                "t__pfo->p[%d].doubleval" % \
                x for x in xrange(var.param_slot,var.param_slot+4)]

class IntType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            return [ "%d" % var.value] 
        else:
            return [
                "t__pfo->p[%d].intval" % var.param_slot]

class GradientType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            raise TranslationError(
                "Internal Compiler Error: gradient not initialized as a param")
        else:
            return [ "t__pfo->p[%d].gradient" % var.param_slot]

        return []

class ImageType(Type):
    def __init__(self,**kwds):
        Type.__init__(self,**kwds)

    def init_val(self,var):
        if var.param_slot == -1:
            raise TranslationError(
                "Internal Compiler Error: image not initialized as a param")
        else:
            return [ "t__pfo->p[%d].image" % var.param_slot]

        return []

# these have to be in the indexes given by the constants above
typeObjectList = [
    IntType(id=Bool, suffix="b",printf="%d",typename="bool",
         default=0,cname="int"),
    
    IntType(id=Int,suffix="i",printf="%d",typename="int",
         default=0,cname="int"),

    FloatType(id=Float,suffix="f",printf="%g",typename="float",
         default=0.0,cname="double"),

    ComplexType(id=Complex,suffix="c",typename="complex",
         default=[0.0,0.0],slots=2,cname="double",parts=["_re","_im"]),

    QuadType(id=Color,suffix="C",typename="color",
         default=[0.0,0.0,0.0,0.0],slots=4, cname="double",
         parts=["_re","_i","_j","_k"]),

    Type(id=String,suffix="S",typename="string",
         default="",slots=0,cname="<Error>"),

    QuadType(id=Hyper,suffix="h",typename="hyper",
             default=[0.0,0.0,0.0,0.0],slots=4,cname="double",
             parts=["_re","_i","_j","_k"]),
    
    GradientType(id=Gradient,suffix="G",typename="gradient",
         default=0,cname="void *"),

    ImageType(id=Image,suffix="I", typename="image",
              default=0, cname="void *"),

    Type(id=VoidArray,suffix="av", typename="voidarray",
         default=0, cname="void *"),

    Type(id=IntArray,suffix="ai", typename="intarray",
             default=0, cname="int *"),

    Type(id=FloatArray,suffix="af", typename="floatarray",
             default=0, cname="double *"),
    
    Type(id=ComplexArray,suffix="ac", typename="complexarray",
             default=0, cname="double *"),

    ]

typeList = [
    Bool,
    Int,
    Float,
    Complex,
    Color,
    String,
    Hyper,
    Gradient,
    Image,
    VoidArray,
    IntArray,
    FloatArray,
    ComplexArray]

suffixOfType = {
    Int : "i",
    Float : "f",
    Complex : "c",
    Bool : "b",
    Color : "C",
    String : "S",
    Hyper : "h",
    Gradient : "G",
    Image : "I",
    VoidArray : "av",
    IntArray : "ai",
    FloatArray : "af",
    ComplexArray : "ac"
    }

_typeOfStr = {
    "int" : Int,
    "float" : Float,
    "complex" : Complex,
    "bool" : Bool,
    "color" : Color,
    "string" : String,
    "hyper" : Hyper,
    "grad" : Gradient,
    "image" : Image,
    "array" : VoidArray,
    "int array" : IntArray,
    "float array" : FloatArray,
    "complex array" : ComplexArray
    }

_strOfType = {
    Int : "int",
    Float : "float",
    Complex : "complex",
    Bool : "bool",
    Color : "color",
    None : "none",
    String : "string",
    Hyper : "hyper",
    Gradient : "grad",
    Image : "image",
    VoidArray: "array",
    IntArray: "int array",
    FloatArray: "float array",
    ComplexArray: "complex array"
   }

_slotsForType = {
    Int: 1,
    Float : 1,
    Complex: 2,
    Bool : 1,
    Color : 4,
    String : 0,
    Hyper: 4,
    Gradient: 1,
    Image: 1
    # arrays not supported as args
    }

def elementSizeOf(type):
    if type == IntArray:
        size = 4
    elif type == FloatArray:
        size = 8
    elif type == ComplexArray:
        size = 8
    else:
        raise TranslationError("invalid allocation type %s" % type)
    
    return size

def arrayTypeOf(t,node=None):
    if t == Int:
        return IntArray
    if t == Float:
        return FloatArray
    if t == Complex:
        return ComplexArray
    
    # there is no array type, make a friendly error
    if not node:
        pos = ""
    else:
        pos = "%d: " % node.pos
    raise TranslationError(        
        "%sArrays of type %s are not supported" % (pos, strOfType(t)))

def elementTypeOf(t,node=None):
    if t == IntArray:
        return Int
    if t == FloatArray:
        return Float
    if t == ComplexArray:
        return Complex
    
    # there is no array type, make a friendly error
    if not node:
        pos = ""
    else:
        pos = "%d: " % node.pos
    raise TranslationError(        
        "%sArrays of type %s are not supported" % (pos, strOfType(t)))


def typeOfStr(tname):
    if not tname: return None
    return _typeOfStr[string.lower(tname)]

def strOfType(t):
    return _strOfType[t]

def default_value(t):
    return typeObjectList[t].default

def slotsForType(t):
    return typeObjectList[t].slots

_canBeCast = [
    # rows are from, columns are to
    # Bool Int Float Complex Color String Hyper Gradient Image VoidArray, IntArray FloatArray ComplexArray
    [ 1,   1,  1,    1,      0,    0,     1,    0,       0,    0,         0,       0,         0,          ], # Bool
    [ 1,   1,  1,    1,      0,    0,     1,    0,       0,    0,         0,       0,         0,          ], # Int
    [ 1,   0,  1,    1,      0,    0,     1,    0,       0,    0,         0,       0,         0,          ], # Float
    [ 1,   0,  0,    1,      0,    0,     1,    0,       0,    0,         0,       0,         0,          ], # Complex
    [ 0,   0,  0,    0,      1,    0,     0,    0,       0,    0,         0,       0,         0,          ], # Color
    [ 0,   0,  0,    0,      0,    1,     0,    0,       0,    0,         0,       0,         0,          ], # String
    [ 1,   0,  0,    0,      0,    0,     1,    0,       0,    0,         0,       0,         0,          ], # Hyper
    [ 0,   0,  0,    0,      0,    0,     0,    1,       0,    0,         0,       0,         0,          ], # Gradient
    [ 0,   0,  0,    0,      0,    0,     0,    0,       1,    0,         0,       0,         0,          ], # Image
    [ 0,   0,  0,    0,      0,    0,     0,    0,       0,    1,         1,       1,         1,          ], # VoidArray
    [ 0,   0,  0,    0,      0,    0,     0,    0,       0,    0,         1,       0,         0,          ], # IntArray
    [ 0,   0,  0,    0,      0,    0,     0,    0,       0,    0,         0,       1,         0,          ], # FloatArray
    [ 0,   0,  0,    0,      0,    0,     0,    0,       0,    0,         0,       0,         1,          ]  # ComplexArray
    ]

def canBeCast(t1,t2):
    ' can t1 be cast to t2?'
    if t1 == None or t2 == None:
        return 0
    return _canBeCast[t1][t2]

# a convenient place to put this.
class TranslationError(exceptions.Exception):
    def __init__(self,msg):
        exceptions.Exception.__init__(self,msg)
        self.msg = msg

class InternalCompilerError(TranslationError):
    def __init__(self,msg):
        TranslationError.__init__("Internal Compiler Error:" + msg)
    
import stdlib

class Func:
    def __init__(self,args,ret,fname,pos=-1):
        self.args = args
        self.implicit_args = []
        self.ret = ret
        self.pos = pos
        self.set_func(fname)
        
    def __copy__(self):
        c = Func(self.args,self.ret,self.fname,self.pos)
        c.implicit_args = copy.copy(self.implicit_args)
        if hasattr(self,"override_name"):
            c.set_override_name(self.override_name)
        if hasattr(self,"caption"):
            c.caption = self.caption
        return c
    
    def first(self):
        return self

    def set_implicit_arg(self,arg):
        self.implicit_args.append(arg)

    def set_override_name(self,name):
        self.override_name = name
        
    def set_func(self,fname):
        # compute the name of the stdlib function to call
        # this is similar in purpose to C++ name mangling
        if fname == None:
            self.genFunc = None
        else:
            typed_fname = fname + "_"
            for arg in self.args:
                typed_fname = typed_fname + suffixOfType[arg]
            typed_fname = typed_fname + "_" + suffixOfType[self.ret]
        
            self.genFunc = stdlib.__dict__.get(typed_fname,typed_fname)

        self.cname = fname
        self.fname = fname
        
    def matchesArgs(self, potentialArgs):
        if len(potentialArgs) != len(self.args):
            return False
        i = 0
        for arg in self.args:
            if not canBeCast(potentialArgs[i],arg):
                return False
            i = i + 1
        return True 

class Var:
    def __init__(self,type,value=None,pos=-1,**kwds):
        #assert(type_ != None)
        #assert(isinstance(pos,types.IntType))
        self._set_type(type)
        if value == None:
            self.value = self._typeobj.default
        else:
            self.value = value
        self.pos = pos
        self.cname = None
        self.__doc__ = kwds.get("doc")
        self.declared = False
        self.param_slot = -1
        
    def _get_is_temp(self):
        return False
    is_temp = property(_get_is_temp)

    def _get_type(self):
        return self._typeobj.typeid

    def _set_type(self,t):
        self._typeobj = typeObjectList[t]

    type = property(_get_type, _set_type)

    def _get_ctype(self):
        return self._typeobj.cname

    ctype = property(_get_ctype)
    
    def struct_name(self):
        return "t__pfo->" + self.cname
    
    def first(self):
        return self
        
    def __str__(self):
        return "%s %s (%d)" % (strOfType(self.type), self.value, self.pos)

    def init_val(self):
        try:
            return self._typeobj.init_val(self)
        except AttributeError:
            print "%s type for %s" % (self._typeobj.typename, self.cname)
            raise

    def _get_part_names(self):
        return self._typeobj.part_names

    part_names = property(_get_part_names)
    
class Temp(Var):
    def __init__(self,type_,name):
        Var.__init__(self,type_)
        self.cname = name

    def _get_is_temp(self):
        return True

    is_temp = property(_get_is_temp)

