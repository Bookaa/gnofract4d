#!/usr/bin/env python

import sys
from fract4d import fc
from fract4d import fractal

def func2():
    file_ = sys.stdin.readline().strip()
    func_ = sys.stdin.readline().strip()
    prefix_ = sys.stdin.readline().strip()
    if prefix_ == 'None':
        prefix_ = None
    print 'get <%s> <%s> <%s>' % (file_, func_, prefix_)
    
    compiler = fc.instance
    compiler.leave_dirty = True

    formula = compiler.get_formula(file_, func_, prefix_)
    params = formula.symbols.default_params()
    paramtypes = formula.symbols.type_of_params()
    print 'params', params
    print 'paramtypes', paramtypes

    defaults_items = formula.defaults.items()
    symbols_func_names = formula.symbols.func_names()
    symbols_param_names = formula.symbols.param_names()
    
    symbol_table = formula.symbols
    op = symbol_table.order_of_params()
    
    dict2 = {}
    for a,b in formula.symbols.items():
        try:
            cname = b[0].cname
            dict2[a] = cname
        except:
            pass

    dict3 = {}
    for a,b in formula.symbols.items():
        try:
            typ = b.type
            dict3[a] = typ
        except:
            pass

    dict_ = {'params' : params, 'paramtypes' : paramtypes, 'defaults_items' : defaults_items,
             'symbols_func_names' : symbols_func_names,
             'symbols_param_names' : symbols_param_names,
             'op' : op,
             'cnames' : dict2,
             'types' : dict3
             }
    import json
    sjson = json.dumps(dict_)
    print 'next is json'
    print sjson


def docompile():
    stype = sys.stdin.readline().strip()
    if stype == '2':
        return func2()
    print 'stype : <%s>' % stype
    
    hash = sys.stdin.readline().strip()
    
    txt = sys.stdin.read()
    # print 'hash:<%s>' % hash
    # print 'txt:<%s>' % txt
    
    compiler = fc.instance
    compiler.leave_dirty = True

    t = fractal.T(compiler)

    outputfile = t.load_and_compile(hash, txt)
    if outputfile:
        print 'success, compile to %s' % outputfile
        


if __name__ == '__main__':
    docompile()
