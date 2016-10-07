# a class to hold a formula and all the parameter settings which go with it

class T:
    def __init__(self,compiler,prefix=None):
        self.compiler = compiler
        self.formula = None
        self.funcName = None
        self.funcFile = None
        self.dirty = False
        self.prefix = prefix

        self.paramlist2 = {} # bookaa : {name : value}


    def set_formula_text_1(self, buftext, formtype, gradient):
        (func, form) = self.compiler.add_inline_formula(buftext, formtype)
        #self.set_formula(file,func,gradient)
        formula = self.compiler.get_formula_3(form, formtype, self.prefix)
        # formula = self.compiler.get_formula(file,func,self.prefix)

        if formula == None:
            raise ValueError("no such formula: %s:%s" % (file, func))

        self.formula = formula
        self.funcName = func
        self.funcFile = None




