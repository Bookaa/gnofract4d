#!/usr/bin/env python

import sys
from fract4d import fc
from fract4d import fractal, fracttypes

def func2(sbody):
    file_ = sys.stdin.readline().strip()
    func_ = sys.stdin.readline().strip()
    prefix_ = sys.stdin.readline().strip()
    if prefix_ == 'None':
        prefix_ = None
    print 'get <%s> <%s> <%s>' % (file_, func_, prefix_)

    compiler = fc.instance
    compiler.leave_dirty = True

    if sbody:
        formulas = compiler.parse_file(sbody)
        ff = fc.FormulaFile(formulas,sbody,None,'')
        ff.file_backed = False
        compiler.files[file_] = ff

    formula = compiler.get_formula(file_, func_, prefix_)
    params = formula.symbols.default_params()
    paramtypes = formula.symbols.type_of_params()
    # print 'params', params
    # print 'paramtypes', paramtypes

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

    dict4 = {}
    for a,b in formula.symbols.items():
        try:
            sym = b.first()
            dict4[a] = isinstance(sym, fracttypes.Func)
        except:
            pass

    params_ = formula.symbols.parameters()

    dict_params = {}
    for key, param in params_.items():
        if isinstance(param, fracttypes.Var):
            dict_params[key] = {'Var' : (param.type, param.value, param.pos)}
        elif isinstance(param, fracttypes.Func):
            dict_params[key] = {'Func' : (param.args, param.implicit_args, param.ret, param.pos, param.fname)}
        else:
            assert False

    dict_ = {'params' : params, 'paramtypes' : paramtypes, 'defaults_items' : defaults_items,
             'symbols_func_names' : symbols_func_names,
             'symbols_param_names' : symbols_param_names,
             'op' : op,
             'cnames' : dict2,
             'types' : dict3,
             'dict4' : dict4,
             'dict_params' : dict_params,
             'is4D' : formula.is4D(),
             }

    import json
    sjson = json.dumps(dict_)
    print 'next is json'
    print sjson


def docompile():
    stype = sys.stdin.readline().strip()
    if stype == '3':
        sbody_ = sys.stdin.readline().strip()
        import json
        sbody = json.loads(sbody_)
        return func2(str(sbody))
    if stype == '2':
        return func2('')
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
