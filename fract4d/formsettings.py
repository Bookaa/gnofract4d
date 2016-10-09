# a class to hold a formula and all the parameter settings which go with it

class T:
    def __init__(self,compiler,prefix=None):
        self.compiler = compiler
        self.formula = None
        self.funcName = None
        self.prefix = prefix

        self.paramlist2 = {} # bookaa : {name : value}


    def set_formula_text_1(self, buftext, formtype, gradient):
        (func, mod) = self.compiler.add_inline_formula(buftext)
        formula = self.compiler.get_formula_3(mod)

        if formula == None:
            raise ValueError("no such formula: %s:%s" % (file, func))

        self.formula = formula
        self.funcName = func




