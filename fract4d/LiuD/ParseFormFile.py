import Ast_GFF
from Ast_GFF import GFF_sample_visitor_01

def getdt(s):
    if s == 'bool':
        return 0
    if s == 'int':
        return 1
    if s == 'float':
        return 2
    if s == 'complex':
        return 3
    if s == 'color':
        return 4
    if s == 'hyper':
        return 6
    return 0

class myprt(Ast_GFF.GFF_out_visitor_01):
    pass

def PrtOneNode(node):
    outlst = []
    outp = Ast_GFF.OutPrt(outlst)
    the = myprt(outp)
    node.walkabout(the)
    outp.newline()
    return '\n'.join(outlst)

def ParseFormuFile_nodeep(s_formufile):
    mod = Ast_GFF.Test_Parse_GFF(s_formufile)
    if not mod:
        return
    formulas = {}
    for v in mod.vlst:
        if isinstance(v, Ast_GFF.GFF_formu):
            leaf = v.n.strip()
            text = PrtOneNode(v)
            formulas[leaf] = text
    return formulas

def ParseFormuFile_deep(s_formufile):
    if True:
        parser = Ast_GFF.Parser(s_formufile)
        mod = parser.handle_formu_deep()
        if mod.n.strip() == 'CGNewton3':
            # replace with I support format
            src = '''CGNewton3 {
    init:
        z = (1.0, 1.0)
    loop:
        z2 = z * z
        z3 = z * z2
        z = z - @p1 * (z3 - #pixel) / (3.0 * z2)
    bailout:
        0.0001 < |z3 - #pixel|

    default:
    complex param p1
        default = (0.66253178213589414, -0.22238807443609804)
    endparam
    }'''
            parser = Ast_GFF.Parser(src)
            mod = parser.handle_formu_deep()
    else:
        mod = Ast_GFF.Test_Parse_GFF(s_formufile)
    if not mod:
        return
    #the = mywalk()
    #dict_ = mod.walkabout(the)
    return mod

