# a class to hold a formula and all the parameter settings which go with it

class T:
    def __init__(self):
        self.formula = None
        self.paramlist2 = {} # bookaa : {name : value}


    def set_formula_text_1(self, buftext):
        (func, mod) = add_inline_formula(buftext)
        formula = TT(mod)

        if formula == None:
            raise ValueError("no such formula: %s:%s" % (file, func))

        self.formula = formula


class TT:
    def __init__(self, mod):
        self.mod = mod
    def GetDefaultValues(self):
        import fractal
        return fractal.GetDefaultVals(self.mod)


def add_inline_formula(formbody):
    # formbody contains a string containing the contents of a formula
    from LiuD import ParseFormFile
    mod = ParseFormFile.ParseFormuFile_deep(formbody)
    name = mod.n.strip()
    return name, mod
