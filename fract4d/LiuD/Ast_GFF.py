# auto generate code, LiuTaoTao

from lib import *

class GFF_Module:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_Module(self)


class GFF_commentblk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_commentblk(self)


class GFF_AnyLine:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_AnyLine(self)


class GFF_formu:
    def __init__(self, n, vq, vlst):
        self.n = n
        self.vq = vq
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_formu(self)


class GFF_formu_deep:
    def __init__(self, n, vq, vlst):
        self.n = n
        self.vq = vq
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_formu_deep(self)


class GFF_para:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_para(self)


class GFF_init_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_init_blk(self)


class GFF_loop_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_loop_blk(self)


class GFF_bailout_blk:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_bailout_blk(self)


class GFF_default_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_default_blk(self)


class GFF_final_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_final_blk(self)


class GFF_anotherfmt:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def walkabout(self, visitor):
        return visitor.visit_anotherfmt(self)


class GFF_dt_param:
    def __init__(self, v1, v2, vlst):
        self.v1 = v1
        self.v2 = v2
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_dt_param(self)


class GFF_dt_func:
    def __init__(self, v, n, vlst):
        self.v = v
        self.n = n
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_dt_func(self)


class GFF_general_func:
    def __init__(self, n, vlst):
        self.n = n
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_general_func(self)


class GFF_general_param:
    def __init__(self, n, vlst):
        self.n = n
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_general_param(self)


class GFF_xcenter:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_xcenter(self)


class GFF_zcenter:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_zcenter(self)


class GFF_wcenter:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_wcenter(self)


class GFF_xycenter:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_xycenter(self)


class GFF_zwcenter:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_zwcenter(self)


class GFF_xzangle:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_xzangle(self)


class GFF_ywangle:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_ywangle(self)


class GFF_magnitude:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_magnitude(self)


class GFF_maxiter:
    def __init__(self, i):
        self.i = i

    def walkabout(self, visitor):
        return visitor.visit_maxiter(self)


class GFF_df_title:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_df_title(self)


class GFF_df_caption:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_df_caption(self)


class GFF_df_default:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_df_default(self)


class GFF_df_hint:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_df_hint(self)


class GFF_df_enum:
    def __init__(self, slst):
        self.slst = slst

    def walkabout(self, visitor):
        return visitor.visit_df_enum(self)


class GFF_df_argtype:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_df_argtype(self)


class GFF_stmt:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_stmt(self)


class GFF_AssignDT:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_AssignDT(self)


class GFF_assign:
    def __init__(self, vq, vlst, v):
        self.vq = vq
        self.vlst = vlst
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_assign(self)


class GFF_nameq:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_nameq(self)


class GFF_assign_complex:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_assign_complex(self)


class GFF_dest_real:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_dest_real(self)


class GFF_dest_imag:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_dest_imag(self)


class GFF_declare:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_declare(self)


class GFF_if_stmt:
    def __init__(self, v1, v2, vlst, vq):
        self.v1 = v1
        self.v2 = v2
        self.vlst = vlst
        self.vq = vq

    def walkabout(self, visitor):
        return visitor.visit_if_stmt(self)


class GFF_while_stmt:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_while_stmt(self)


class GFF_elseifblk:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_elseifblk(self)


class GFF_elseblk:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_elseblk(self)


class GFF_stmtblk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_stmtblk(self)


class GFF_String:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_String(self)


class GFF_Numi:
    def __init__(self, i):
        self.i = i

    def walkabout(self, visitor):
        return visitor.visit_Numi(self)


class GFF_NegNumi:
    def __init__(self, i):
        self.i = i

    def walkabout(self, visitor):
        return visitor.visit_NegNumi(self)


class GFF_Number:
    def __init__(self, f):
        self.f = f

    def walkabout(self, visitor):
        return visitor.visit_Number(self)


class GFF_NegNumber:
    def __init__(self, f):
        self.f = f

    def walkabout(self, visitor):
        return visitor.visit_NegNumber(self)


class GFF_Num_Complex:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_Num_Complex(self)


class GFF_Num_Hyper:
    def __init__(self, v1, v2, v3, v4):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def walkabout(self, visitor):
        return visitor.visit_Num_Hyper(self)


class GFF_bool_value:
    def __init__(self, s):
        self.s = s

    def walkabout(self, visitor):
        return visitor.visit_bool_value(self)


class GFF_not_value:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_not_value(self)


class GFF_value2:
    def __init__(self, v1, s, v3):
        self.v1 = v1
        self.s = s
        self.v3 = v3

    def walkabout(self, visitor):
        return visitor.visit_value2(self)


class GFF_neg_value:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_neg_value(self)


class GFF_EnclosedValue:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_EnclosedValue(self)


class GFF_AbsSigned:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_AbsSigned(self)


class GFF_funccall:
    def __init__(self, v, vq):
        self.v = v
        self.vq = vq

    def walkabout(self, visitor):
        return visitor.visit_funccall(self)


class GFF_callparam:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_callparam(self)


class GFF_Name0:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name0(self)


class GFF_Name1:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name1(self)


class GFF_Name2:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name2(self)

class GFF_sample_visitor_00:
    def visit_Module(self, node): pass
    def visit_commentblk(self, node): pass
    def visit_AnyLine(self, node): pass
    def visit_formu(self, node): pass
    def visit_formu_deep(self, node): pass
    def visit_para(self, node): pass
    def visit_init_blk(self, node): pass
    def visit_loop_blk(self, node): pass
    def visit_bailout_blk(self, node): pass
    def visit_default_blk(self, node): pass
    def visit_final_blk(self, node): pass
    def visit_anotherfmt(self, node): pass
    def visit_dt_param(self, node): pass
    def visit_dt_func(self, node): pass
    def visit_general_func(self, node): pass
    def visit_general_param(self, node): pass
    def visit_xcenter(self, node): pass
    def visit_zcenter(self, node): pass
    def visit_wcenter(self, node): pass
    def visit_xycenter(self, node): pass
    def visit_zwcenter(self, node): pass
    def visit_xzangle(self, node): pass
    def visit_ywangle(self, node): pass
    def visit_magnitude(self, node): pass
    def visit_maxiter(self, node): pass
    def visit_df_title(self, node): pass
    def visit_df_caption(self, node): pass
    def visit_df_default(self, node): pass
    def visit_df_hint(self, node): pass
    def visit_df_enum(self, node): pass
    def visit_df_argtype(self, node): pass
    def visit_stmt(self, node): pass
    def visit_AssignDT(self, node): pass
    def visit_assign(self, node): pass
    def visit_nameq(self, node): pass
    def visit_assign_complex(self, node): pass
    def visit_dest_real(self, node): pass
    def visit_dest_imag(self, node): pass
    def visit_declare(self, node): pass
    def visit_if_stmt(self, node): pass
    def visit_while_stmt(self, node): pass
    def visit_elseifblk(self, node): pass
    def visit_elseblk(self, node): pass
    def visit_stmtblk(self, node): pass
    def visit_String(self, node): pass
    def visit_Numi(self, node): pass
    def visit_NegNumi(self, node): pass
    def visit_Number(self, node): pass
    def visit_NegNumber(self, node): pass
    def visit_Num_Complex(self, node): pass
    def visit_Num_Hyper(self, node): pass
    def visit_bool_value(self, node): pass
    def visit_not_value(self, node): pass
    def visit_value2(self, node): pass
    def visit_neg_value(self, node): pass
    def visit_EnclosedValue(self, node): pass
    def visit_AbsSigned(self, node): pass
    def visit_funccall(self, node): pass
    def visit_callparam(self, node): pass
    def visit_Name0(self, node): pass
    def visit_Name1(self, node): pass
    def visit_Name2(self, node): pass

class GFF_sample_visitor_01:
    def visit_Module(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_commentblk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_AnyLine(self, node):
        pass
    def visit_formu(self, node):
        if node.vq is not None:
            node.vq.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
    def visit_formu_deep(self, node):
        if node.vq is not None:
            node.vq.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
    def visit_para(self, node):
        pass
    def visit_init_blk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_loop_blk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_bailout_blk(self, node):
        node.v.walkabout(self)
    def visit_default_blk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_final_blk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_anotherfmt(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
        node.v3.walkabout(self)
    def visit_dt_param(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
    def visit_dt_func(self, node):
        node.v.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
    def visit_general_func(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_general_param(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_xcenter(self, node):
        node.v.walkabout(self)
    def visit_zcenter(self, node):
        node.v.walkabout(self)
    def visit_wcenter(self, node):
        node.v.walkabout(self)
    def visit_xycenter(self, node):
        node.v.walkabout(self)
    def visit_zwcenter(self, node):
        node.v.walkabout(self)
    def visit_xzangle(self, node):
        node.v.walkabout(self)
    def visit_ywangle(self, node):
        node.v.walkabout(self)
    def visit_magnitude(self, node):
        node.v.walkabout(self)
    def visit_maxiter(self, node):
        pass
    def visit_df_title(self, node):
        pass
    def visit_df_caption(self, node):
        pass
    def visit_df_default(self, node):
        node.v.walkabout(self)
    def visit_df_hint(self, node):
        pass
    def visit_df_enum(self, node):
        pass
    def visit_df_argtype(self, node):
        node.v.walkabout(self)
    def visit_stmt(self, node):
        node.v.walkabout(self)
    def visit_AssignDT(self, node):
        pass
    def visit_assign(self, node):
        if node.vq is not None:
            node.vq.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
        node.v.walkabout(self)
    def visit_nameq(self, node):
        node.v.walkabout(self)
    def visit_assign_complex(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_dest_real(self, node):
        node.v.walkabout(self)
    def visit_dest_imag(self, node):
        node.v.walkabout(self)
    def visit_declare(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_if_stmt(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
        if node.vq is not None:
            node.vq.walkabout(self)
    def visit_while_stmt(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_elseifblk(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_elseblk(self, node):
        node.v.walkabout(self)
    def visit_stmtblk(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_String(self, node):
        pass
    def visit_Numi(self, node):
        pass
    def visit_NegNumi(self, node):
        pass
    def visit_Number(self, node):
        pass
    def visit_NegNumber(self, node):
        pass
    def visit_Num_Complex(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_Num_Hyper(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
        node.v3.walkabout(self)
        node.v4.walkabout(self)
    def visit_bool_value(self, node):
        pass
    def visit_not_value(self, node):
        node.v.walkabout(self)
    def visit_value2(self, node):
        node.v1.walkabout(self)
        node.v3.walkabout(self)
    def visit_neg_value(self, node):
        node.v.walkabout(self)
    def visit_EnclosedValue(self, node):
        node.v.walkabout(self)
    def visit_AbsSigned(self, node):
        node.v.walkabout(self)
    def visit_funccall(self, node):
        node.v.walkabout(self)
        if node.vq is not None:
            node.vq.walkabout(self)
    def visit_callparam(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_Name0(self, node):
        pass
    def visit_Name1(self, node):
        pass
    def visit_Name2(self, node):
        pass

class GFF_out_visitor_01:
    def __init__(self, outp):
        self.outp = outp
    def visit_Module(self, node):
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
    def visit_commentblk(self, node):
        self.outp.puts('comment {')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
        self.outp.puts('}')
    def visit_AnyLine(self, node):
        self.outp.puts(node.n)
    def visit_formu(self, node):
        self.outp.puts(node.n)
        if node.vq is not None:
            node.vq.walkabout(self)
        self.outp.puts('{')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
        self.outp.puts('}')
    def visit_formu_deep(self, node):
        self.outp.puts(node.n)
        if node.vq is not None:
            node.vq.walkabout(self)
        self.outp.puts('{')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
        self.outp.puts('}')
    def visit_para(self, node):
        self.outp.puts('(')
        self.outp.puts(node.n)
        self.outp.puts(')')
    def visit_init_blk(self, node):
        self.outp.puts('init:')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
    def visit_loop_blk(self, node):
        self.outp.puts('loop:')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
    def visit_bailout_blk(self, node):
        self.outp.puts('bailout:')
        self.outp.newline()
        node.v.walkabout(self)
    def visit_default_blk(self, node):
        self.outp.puts('default:')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
    def visit_final_blk(self, node):
        self.outp.puts('final:')
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
    def visit_anotherfmt(self, node):
        node.v1.walkabout(self)
        self.outp.puts(':')
        self.outp.newline()
        node.v2.walkabout(self)
        node.v3.walkabout(self)
    def visit_dt_param(self, node):
        node.v1.walkabout(self)
        self.outp.puts('param')
        node.v2.walkabout(self)
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
        self.outp.puts('endparam')
    def visit_dt_func(self, node):
        node.v.walkabout(self)
        self.outp.puts('func')
        self.outp.puts(node.n)
        self.outp.newline()
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
        self.outp.puts('endfunc')
    def visit_general_func(self, node):
        self.outp.puts('func')
        self.outp.puts(node.n)
        for tem1 in node.vlst:
            tem1.walkabout(self)
        self.outp.puts('endfunc')
    def visit_general_param(self, node):
        self.outp.puts('param')
        self.outp.puts(node.n)
        for tem1 in node.vlst:
            tem1.walkabout(self)
        self.outp.puts('endparam')
    def visit_xcenter(self, node):
        self.outp.puts('xcenter =')
        node.v.walkabout(self)
    def visit_zcenter(self, node):
        self.outp.puts('zcenter =')
        node.v.walkabout(self)
    def visit_wcenter(self, node):
        self.outp.puts('wcenter =')
        node.v.walkabout(self)
    def visit_xycenter(self, node):
        self.outp.puts('xycenter =')
        node.v.walkabout(self)
    def visit_zwcenter(self, node):
        self.outp.puts('zwcenter =')
        node.v.walkabout(self)
    def visit_xzangle(self, node):
        self.outp.puts('xzangle =')
        node.v.walkabout(self)
    def visit_ywangle(self, node):
        self.outp.puts('ywangle =')
        node.v.walkabout(self)
    def visit_magnitude(self, node):
        self.outp.puts('magnitude =')
        node.v.walkabout(self)
    def visit_maxiter(self, node):
        self.outp.puts('maxiter =')
        self.outp.puts(node.i)
    def visit_df_title(self, node):
        self.outp.puts('title =')
        self.outp.putss(node.s)
    def visit_df_caption(self, node):
        self.outp.puts('caption =')
        self.outp.putss(node.s)
    def visit_df_default(self, node):
        self.outp.puts('default =')
        node.v.walkabout(self)
    def visit_df_hint(self, node):
        self.outp.puts('hint =')
        self.outp.putss(node.s)
    def visit_df_enum(self, node):
        self.outp.puts('enum =')
        for tem1 in node.slst:
            self.outp.puts(tem1)
    def visit_df_argtype(self, node):
        self.outp.puts('argtype =')
        node.v.walkabout(self)
    def visit_stmt(self, node):
        node.v.walkabout(self)
    def visit_AssignDT(self, node):
        self.outp.puts(node.s)
    def visit_assign(self, node):
        if node.vq is not None:
            node.vq.walkabout(self)
        for tem1 in node.vlst:
            tem1.walkabout(self)
        node.v.walkabout(self)
    def visit_nameq(self, node):
        node.v.walkabout(self)
        self.outp.puts('=')
    def visit_assign_complex(self, node):
        node.v1.walkabout(self)
        self.outp.puts('=')
        node.v2.walkabout(self)
    def visit_dest_real(self, node):
        self.outp.puts('real(')
        node.v.walkabout(self)
        self.outp.puts(')')
    def visit_dest_imag(self, node):
        self.outp.puts('imag(')
        node.v.walkabout(self)
        self.outp.puts(')')
    def visit_declare(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_if_stmt(self, node):
        self.outp.puts('if')
        node.v1.walkabout(self)
        self.outp.newline()
        node.v2.walkabout(self)
        for tem1 in node.vlst:
            tem1.walkabout(self)
        if node.vq is not None:
            node.vq.walkabout(self)
        self.outp.newline()
        self.outp.puts('endif')
    def visit_while_stmt(self, node):
        self.outp.puts('while')
        node.v1.walkabout(self)
        self.outp.newline()
        node.v2.walkabout(self)
        self.outp.puts('endwhile')
    def visit_elseifblk(self, node):
        self.outp.puts('elseif')
        node.v1.walkabout(self)
        self.outp.newline()
        node.v2.walkabout(self)
    def visit_elseblk(self, node):
        self.outp.puts('else')
        self.outp.newline()
        node.v.walkabout(self)
    def visit_stmtblk(self, node):
        for tem1 in node.vlst:
            tem1.walkabout(self)
            self.outp.newline()
    def visit_String(self, node):
        self.outp.putss(node.s)
    def visit_Numi(self, node):
        self.outp.puts(node.i)
    def visit_NegNumi(self, node):
        self.outp.puts('-')
        self.outp.lnk()
        self.outp.puts(node.i)
    def visit_Number(self, node):
        self.outp.puts(node.f)
    def visit_NegNumber(self, node):
        self.outp.puts('-')
        self.outp.lnk()
        self.outp.puts(node.f)
    def visit_Num_Complex(self, node):
        self.outp.puts('(')
        node.v1.walkabout(self)
        self.outp.puts(',')
        node.v2.walkabout(self)
        self.outp.puts(')')
    def visit_Num_Hyper(self, node):
        self.outp.puts('(')
        node.v1.walkabout(self)
        self.outp.puts(',')
        node.v2.walkabout(self)
        self.outp.puts(',')
        node.v3.walkabout(self)
        self.outp.puts(',')
        node.v4.walkabout(self)
        self.outp.puts(')')
    def visit_bool_value(self, node):
        self.outp.puts(node.s)
    def visit_not_value(self, node):
        self.outp.puts('!')
        node.v.walkabout(self)
    def visit_value2(self, node):
        node.v1.walkabout(self)
        self.outp.puts(node.s)
        node.v3.walkabout(self)
    def visit_neg_value(self, node):
        self.outp.puts('-')
        self.outp.lnk()
        node.v.walkabout(self)
    def visit_EnclosedValue(self, node):
        self.outp.puts('(')
        node.v.walkabout(self)
        self.outp.puts(')')
    def visit_AbsSigned(self, node):
        self.outp.puts('|')
        node.v.walkabout(self)
        self.outp.puts('|')
    def visit_funccall(self, node):
        node.v.walkabout(self)
        self.outp.puts('(')
        if node.vq is not None:
            node.vq.walkabout(self)
        self.outp.puts(')')
    def visit_callparam(self, node):
        tem1 = 0
        for tem2 in node.vlst:
            if tem1 > 0:
                self.outp.puts(',')
            tem1 = 1
            tem2.walkabout(self)
    def visit_Name0(self, node):
        self.outp.puts(node.n)
    def visit_Name1(self, node):
        self.outp.puts('#')
        self.outp.lnk()
        self.outp.puts(node.n)
    def visit_Name2(self, node):
        self.outp.puts('@')
        self.outp.lnk()
        self.outp.puts(node.n)


class Parser(Parser00):

    def __init__(self, srctxt):
        Parser00.__init__(self, srctxt)

        self.skips = [
            IgnoreCls(' \t\n', [';.*', '{-(.|\\n)*?-}', '\\\\\\n']),
        ]
        self.lex_ANYLINE = HowRe(r'[^}\n]+')
        self.lex_ANYNAME = HowRe(r'[^({\n]+')
        self.lex_NUMBER_INT = HowRe(r'0|[1-9]\d*')
        self.lex_NUM_DOUBLE = HowRe(r'\d*\.\d+(e(-)?\d+)?|\d+\.')
        self.lex_STR = HowRe(r'"(.|\n)*?"')
    
    def handle_ANYLINE(self, s = None):
        return self.handle_Lex(self.lex_ANYLINE, s)
    
    def handle_ANYNAME(self, s = None):
        return self.handle_Lex(self.lex_ANYNAME, s)
    
    def handle_NUMBER_INT(self):
        s = self.handle_Lex(self.lex_NUMBER_INT)
        return None if s is None else int(s)
    
    def handle_NUM_DOUBLE(self):
        return self.handle_Lex(self.lex_NUM_DOUBLE)
    
    def handle_STR(self):
        return self.handle_string_Lex(self.lex_STR)

    def handle_Module(self):
        self.Skip(0)
        sav0 = self.getpos()
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_blk()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_ENDMARKER() is None:
            self.setpos(sav0)
            return None
        return GFF_Module(vlst)

    def hdl_blk(self):
        v = self.handle_commentblk()
        if v is not None:
            return v
        return self.handle_formu()

    def handle_commentblk(self):
        sav0 = self.getpos()
        if self.handle_NAME('comment') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('{') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_AnyLine()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_OpChar('}') is None:
            self.setpos(sav0)
            return None
        return GFF_commentblk(vlst)

    def handle_AnyLine(self):
        sav0 = self.getpos()
        n = self.handle_ANYLINE()
        if n is None:
            self.setpos(sav0)
            return None
        return GFF_AnyLine(n)

    def handle_formu(self):
        sav0 = self.getpos()
        n = self.handle_ANYNAME()
        if n is None:
            self.setpos(sav0)
            return None
        sav1 = self.getpos()
        self.Skip(0)
        vq = self.handle_para()
        if vq is None:
            self.setpos(sav1)
        self.Skip(0)
        if self.handle_OpChar('{') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav2 = self.getpos()
        while True:
            v3 = self.handle_AnyLine()
            if v3 is None:
                break
            vlst.append(v3)
            sav2 = self.getpos()
            self.Skip(0)
        self.setpos(sav2)
        self.Skip(0)
        if self.handle_OpChar('}') is None:
            self.setpos(sav0)
            return None
        return GFF_formu(n, vq, vlst)

    def handle_formu_deep(self):
        sav0 = self.getpos()
        n = self.handle_ANYNAME()
        if n is None:
            self.setpos(sav0)
            return None
        sav1 = self.getpos()
        self.Skip(0)
        vq = self.handle_para()
        if vq is None:
            self.setpos(sav1)
        self.Skip(0)
        if self.handle_OpChar('{') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav2 = self.getpos()
        while True:
            v3 = self.hdl_labelblk()
            if v3 is None:
                break
            vlst.append(v3)
            sav2 = self.getpos()
            self.Skip(0)
        self.setpos(sav2)
        self.Skip(0)
        if self.handle_OpChar('}') is None:
            self.setpos(sav0)
            return None
        return GFF_formu_deep(n, vq, vlst)

    def handle_para(self):
        sav0 = self.getpos()
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_para(n)

    def hdl_labelblk(self):
        v = self.handle_init_blk()
        if v is not None:
            return v
        v = self.handle_loop_blk()
        if v is not None:
            return v
        v = self.handle_final_blk()
        if v is not None:
            return v
        v = self.handle_default_blk()
        if v is not None:
            return v
        v = self.handle_bailout_blk()
        if v is not None:
            return v
        return self.handle_anotherfmt()

    def handle_init_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('init:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_init_blk(vlst)

    def handle_loop_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('loop:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_loop_blk(vlst)

    def handle_bailout_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('bailout:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_value()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_bailout_blk(v)

    def handle_default_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('default:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_def_item()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_default_blk(vlst)

    def handle_final_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('final:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_final_blk(vlst)

    def handle_anotherfmt(self):
        sav0 = self.getpos()
        v1 = self.handle_stmtblk()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(':') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_stmtblk()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v3 = self.hdl_value()
        if v3 is None:
            self.setpos(sav0)
            return None
        return GFF_anotherfmt(v1, v2, v3)

    def hdl_def_item(self):
        v = self.handle_dt_param()
        if v is not None:
            return v
        v = self.handle_dt_func()
        if v is not None:
            return v
        v = self.handle_general_param()
        if v is not None:
            return v
        v = self.handle_general_func()
        if v is not None:
            return v
        v = self.handle_xcenter()
        if v is not None:
            return v
        v = self.handle_zcenter()
        if v is not None:
            return v
        v = self.handle_wcenter()
        if v is not None:
            return v
        v = self.handle_magnitude()
        if v is not None:
            return v
        v = self.handle_xycenter()
        if v is not None:
            return v
        v = self.handle_zwcenter()
        if v is not None:
            return v
        v = self.handle_xzangle()
        if v is not None:
            return v
        v = self.handle_ywangle()
        if v is not None:
            return v
        return self.handle_maxiter()

    def handle_dt_param(self):
        sav0 = self.getpos()
        v1 = self.handle_AssignDT()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('param') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_Name0()
        if v2 is None:
            v2 = self.handle_Name2()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_df_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_NAME('endparam') is None:
            self.setpos(sav0)
            return None
        return GFF_dt_param(v1, v2, vlst)

    def handle_dt_func(self):
        sav0 = self.getpos()
        v = self.handle_AssignDT()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('func') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_df_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_NAME('endfunc') is None:
            self.setpos(sav0)
            return None
        return GFF_dt_func(v, n, vlst)

    def handle_general_func(self):
        sav0 = self.getpos()
        if self.handle_NAME('func') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_df_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_NAME('endfunc') is None:
            self.setpos(sav0)
            return None
        return GFF_general_func(n, vlst)

    def handle_general_param(self):
        sav0 = self.getpos()
        if self.handle_NAME('param') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_df_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        self.Skip(0)
        if self.handle_NAME('endparam') is None:
            self.setpos(sav0)
            return None
        return GFF_general_param(n, vlst)

    def handle_xcenter(self):
        sav0 = self.getpos()
        if self.handle_NAME('xcenter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_xcenter(v)

    def handle_zcenter(self):
        sav0 = self.getpos()
        if self.handle_NAME('zcenter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_zcenter(v)

    def handle_wcenter(self):
        sav0 = self.getpos()
        if self.handle_NAME('wcenter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_wcenter(v)

    def handle_xycenter(self):
        sav0 = self.getpos()
        if self.handle_NAME('xycenter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_Num_Complex()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_xycenter(v)

    def handle_zwcenter(self):
        sav0 = self.getpos()
        if self.handle_NAME('zwcenter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_Num_Complex()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_zwcenter(v)

    def handle_xzangle(self):
        sav0 = self.getpos()
        if self.handle_NAME('xzangle') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_xzangle(v)

    def handle_ywangle(self):
        sav0 = self.getpos()
        if self.handle_NAME('ywangle') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_ywangle(v)

    def handle_magnitude(self):
        sav0 = self.getpos()
        if self.handle_NAME('magnitude') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_num22()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_magnitude(v)

    def handle_maxiter(self):
        sav0 = self.getpos()
        if self.handle_NAME('maxiter') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        i = self.handle_NUMBER_INT()
        if i is None:
            self.setpos(sav0)
            return None
        return GFF_maxiter(i)

    def hdl_df_stmt(self):
        v = self.handle_df_caption()
        if v is not None:
            return v
        v = self.handle_df_title()
        if v is not None:
            return v
        v = self.handle_df_default()
        if v is not None:
            return v
        v = self.handle_df_hint()
        if v is not None:
            return v
        v = self.handle_df_enum()
        if v is not None:
            return v
        return self.handle_df_argtype()

    def handle_df_title(self):
        sav0 = self.getpos()
        if self.handle_NAME('title') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        s = self.handle_STR()
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_df_title(s)

    def handle_df_caption(self):
        sav0 = self.getpos()
        if self.handle_NAME('caption') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        s = self.handle_STR()
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_df_caption(s)

    def handle_df_default(self):
        sav0 = self.getpos()
        if self.handle_NAME('default') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_df_value()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_df_default(v)

    def handle_df_hint(self):
        sav0 = self.getpos()
        if self.handle_NAME('hint') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        s = self.handle_STR()
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_df_hint(s)

    def hdl_df_value(self):
        v = self.handle_funccall()
        if v is not None:
            return v
        v = self.handle_Name1()
        if v is not None:
            return v
        v = self.handle_Name2()
        if v is not None:
            return v
        v = self.handle_Name0()
        if v is not None:
            return v
        v = self.hdl_Number00()
        if v is not None:
            return v
        v = self.hdl_Number01()
        if v is not None:
            return v
        v = self.handle_String()
        if v is not None:
            return v
        v = self.handle_Num_Complex()
        if v is not None:
            return v
        return self.handle_Num_Hyper()

    def handle_df_enum(self):
        sav0 = self.getpos()
        if self.handle_NAME('enum') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        slst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_STR()
            if v3 is None:
                break
            slst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_df_enum(slst)

    def handle_df_argtype(self):
        sav0 = self.getpos()
        if self.handle_NAME('argtype') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_AssignDT()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_df_argtype(v)

    def hdl_stmt_1(self):
        v = self.handle_assign()
        if v is not None:
            return v
        v = self.handle_assign_complex()
        if v is not None:
            return v
        v = self.handle_declare()
        if v is not None:
            return v
        v = self.handle_if_stmt()
        if v is not None:
            return v
        return self.handle_while_stmt()

    def handle_stmt(self):
        sav0 = self.getpos()
        v = self.hdl_stmt_1()
        if v is None:
            self.setpos(sav0)
            return None
        sav1 = self.getpos()
        self.Skip(0)
        self.handle_OpChar(',')
        return GFF_stmt(v)

    def handle_AssignDT(self):
        sav0 = self.getpos()
        s = self.handle_NAME('float')
        if s is None:
            s = self.handle_NAME('color')
        if s is None:
            s = self.handle_NAME('complex')
        if s is None:
            s = self.handle_NAME('int')
        if s is None:
            s = self.handle_NAME('bool')
        if s is None:
            s = self.handle_NAME('hyper')
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_AssignDT(s)

    def handle_assign(self):
        sav0 = self.getpos()
        vq = self.handle_AssignDT()
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_nameq()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        if not vlst:
            self.setpos(sav0)
            return None
        self.setpos(sav1)
        self.Skip(0)
        v = self.hdl_value()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_assign(vq, vlst, v)

    def handle_nameq(self):
        sav0 = self.getpos()
        v = self.handle_Name0()
        if v is None:
            v = self.handle_Name1()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        return GFF_nameq(v)

    def handle_assign_complex(self):
        sav0 = self.getpos()
        v1 = self.handle_dest_real()
        if v1 is None:
            v1 = self.handle_dest_imag()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.hdl_value()
        if v2 is None:
            self.setpos(sav0)
            return None
        return GFF_assign_complex(v1, v2)

    def handle_dest_real(self):
        sav0 = self.getpos()
        if self.handle_NAME('real') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_Name0()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_dest_real(v)

    def handle_dest_imag(self):
        sav0 = self.getpos()
        if self.handle_NAME('imag') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_Name0()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_dest_imag(v)

    def handle_declare(self):
        sav0 = self.getpos()
        v1 = self.handle_AssignDT()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_Name0()
        if v2 is None:
            self.setpos(sav0)
            return None
        return GFF_declare(v1, v2)

    def handle_if_stmt(self):
        sav0 = self.getpos()
        if self.handle_NAME('if') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v1 = self.hdl_value()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_stmtblk()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_elseifblk()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        sav2 = self.getpos()
        self.Skip(0)
        vq = self.handle_elseblk()
        if vq is None:
            self.setpos(sav2)
        self.Skip(0)
        if self.handle_NAME('endif') is None:
            self.setpos(sav0)
            return None
        return GFF_if_stmt(v1, v2, vlst, vq)

    def handle_while_stmt(self):
        sav0 = self.getpos()
        if self.handle_NAME('while') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v1 = self.hdl_value()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_stmtblk()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('endwhile') is None:
            self.setpos(sav0)
            return None
        return GFF_while_stmt(v1, v2)

    def handle_elseifblk(self):
        sav0 = self.getpos()
        if self.handle_NAME('elseif') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v1 = self.hdl_value()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_stmtblk()
        if v2 is None:
            self.setpos(sav0)
            return None
        return GFF_elseifblk(v1, v2)

    def handle_elseblk(self):
        sav0 = self.getpos()
        if self.handle_NAME('else') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_stmtblk()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_elseblk(v)

    def handle_stmtblk(self):
        sav0 = self.getpos()
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.handle_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GFF_stmtblk(vlst)

    def handle_String(self):
        sav0 = self.getpos()
        s = self.handle_STR()
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_String(s)

    def handle_Numi(self):
        sav0 = self.getpos()
        i = self.handle_NUMBER_INT()
        if i is None:
            self.setpos(sav0)
            return None
        return GFF_Numi(i)

    def handle_NegNumi(self):
        sav0 = self.getpos()
        if self.handle_OpChar('-') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        i = self.handle_NUMBER_INT()
        if i is None:
            self.setpos(sav0)
            return None
        return GFF_NegNumi(i)

    def hdl_Number01(self):
        v = self.handle_Numi()
        if v is not None:
            return v
        return self.handle_NegNumi()

    def handle_Number(self):
        sav0 = self.getpos()
        f = self.handle_NUM_DOUBLE()
        if f is None:
            self.setpos(sav0)
            return None
        return GFF_Number(f)

    def handle_NegNumber(self):
        sav0 = self.getpos()
        if self.handle_OpChar('-') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        f = self.handle_NUM_DOUBLE()
        if f is None:
            self.setpos(sav0)
            return None
        return GFF_NegNumber(f)

    def hdl_Number00(self):
        v = self.handle_Number()
        if v is not None:
            return v
        return self.handle_NegNumber()

    def handle_Num_Complex(self):
        sav0 = self.getpos()
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v1 = self.hdl_value()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(',') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.hdl_value()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_Num_Complex(v1, v2)

    def handle_Num_Hyper(self):
        sav0 = self.getpos()
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v1 = self.hdl_value()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(',') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.hdl_value()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(',') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v3 = self.hdl_value()
        if v3 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(',') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v4 = self.hdl_value()
        if v4 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_Num_Hyper(v1, v2, v3, v4)

    def hdl_num22(self):
        v = self.hdl_Number00()
        if v is not None:
            return v
        return self.hdl_Number01()

    def handle_bool_value(self):
        sav0 = self.getpos()
        s = self.handle_NAME('false')
        if s is None:
            s = self.handle_NAME('true')
        if s is None:
            self.setpos(sav0)
            return None
        return GFF_bool_value(s)

    def handle_not_value(self):
        sav0 = self.getpos()
        if self.handle_OpChar('!') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_value1()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_not_value(v)

    def hdl_value0(self):
        v = self.handle_bool_value()
        if v is not None:
            return v
        v = self.handle_Name1()
        if v is not None:
            return v
        v = self.handle_Name2()
        if v is not None:
            return v
        v = self.handle_Name0()
        if v is not None:
            return v
        v = self.hdl_Number00()
        if v is not None:
            return v
        v = self.hdl_Number01()
        if v is not None:
            return v
        v = self.handle_String()
        if v is not None:
            return v
        v = self.handle_Num_Complex()
        if v is not None:
            return v
        v = self.handle_Num_Hyper()
        if v is not None:
            return v
        return self.handle_not_value()

    def hdl_value1(self):
        v = self.handle_funccall()
        if v is not None:
            return v
        v = self.hdl_value0()
        if v is not None:
            return v
        v = self.handle_EnclosedValue()
        if v is not None:
            return v
        return self.handle_AbsSigned()

    def handle_value2(self):
        v = self.hdl_value1()
        if v is None:
            return None
        return self.step6_value2(v)
    
    def step1_value2(self, v1):
        sav0 = self.getpos()
        self.Skip(0)
        op = self.handle_OpChar('^')
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v1 = GFF_value2(v1, op, v2)
        return self.step1_value2(v1)
    
    def step2_value2(self, v1):
        v1 = self.step1_value2(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.GetOpInLst(['*', '/'])
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step1_value2(v2)
        v1 = GFF_value2(v1, op, v2)
        return self.step2_value2(v1)
    
    def step3_value2(self, v1):
        v1 = self.step2_value2(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.GetOpInLst(['+', '-'])
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step2_value2(v2)
        v1 = GFF_value2(v1, op, v2)
        return self.step3_value2(v1)
    
    def step4_value2(self, v1):
        v1 = self.step3_value2(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.handle_OpChar('%')
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step3_value2(v2)
        v1 = GFF_value2(v1, op, v2)
        return self.step4_value2(v1)
    
    def step5_value2(self, v1):
        v1 = self.step4_value2(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.GetOpInLst(['>=', '>', '<=', '<', '=='])
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step4_value2(v2)
        v1 = GFF_value2(v1, op, v2)
        return self.step5_value2(v1)
    
    def step6_value2(self, v1):
        v1 = self.step5_value2(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.GetOpInLst(['||', '&&'])
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step5_value2(v2)
        v1 = GFF_value2(v1, op, v2)
        return self.step6_value2(v1)

    def hdl_value(self):
        v = self.handle_neg_value()
        if v is not None:
            return v
        return self.handle_value2()

    def handle_neg_value(self):
        sav0 = self.getpos()
        if self.handle_OpChar('-') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_value2()
        if v is None:
            self.setpos(sav0)
            return None
        return GFF_neg_value(v)

    def handle_EnclosedValue(self):
        sav0 = self.getpos()
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_value()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_EnclosedValue(v)

    def handle_AbsSigned(self):
        sav0 = self.getpos()
        if self.handle_OpChar('|') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_value()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('|') is None:
            self.setpos(sav0)
            return None
        return GFF_AbsSigned(v)

    def handle_funccall(self):
        sav0 = self.getpos()
        v = self.hdl_value0()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        sav1 = self.getpos()
        self.Skip(0)
        vq = self.handle_callparam()
        if vq is None:
            self.setpos(sav1)
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GFF_funccall(v, vq)

    def handle_callparam(self):
        sav0 = self.getpos()
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_value()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
            if not self.handle_OpChar(','):
                break
            self.Skip(0)
        if not vlst:
            self.setpos(sav0)
            return None
        self.setpos(sav1)
        return GFF_callparam(vlst)

    def handle_Name0(self):
        sav0 = self.getpos()
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GFF_Name0(n)

    def handle_Name1(self):
        sav0 = self.getpos()
        if self.handle_OpChar('#') is None:
            self.setpos(sav0)
            return None
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GFF_Name1(n)

    def handle_Name2(self):
        sav0 = self.getpos()
        if self.handle_OpChar('@') is None:
            self.setpos(sav0)
            return None
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GFF_Name2(n)

def Test_Parse_GFF(srctxt):
    parser = Parser(srctxt)
    mod = parser.handle_Module()
    if mod is None:
        lastpos, lastlineno, lastcolumn, lastline = parser.GetLast()
        print 'parse error, last pos = %d' % lastpos
        print 'last lineno = %d, column = %d' % (lastlineno, lastcolumn)
        print 'last line :', lastline
    else:
        print 'parse success'
    return mod


def Test_Out_GFF(mod):
    outp = OutPrt()
    the = GFF_out_visitor_01(outp)
    mod.walkabout(the)
    outp.newline()

s_sample_GFF = r'''

Barnsley Type 3 {
; From Michael Barnsley's book Fractals Everywhere, via Fractint
init:
	z = #zwpixel
loop:
	float x2 = real(z) * real(z)
	float y2 = imag(z) * imag(z)
	float xy = real(z) * imag(z)

	if(real(z) > 0)
		z = (x2 - y2 - 1.0, xy * 2.0)
	else
		z = (x2 - y2 - 1.0 + real(#pixel) * real(z), \
		     xy * 2.0 + imag(#pixel) * real(z))
	endif
bailout:
	@bailfunc(z) < @bailout
default:
float param bailout
	default = 4.0
endparam
float func bailfunc
	default = cmag
endfunc
}

'''

if __name__ == '__main__':
    mod = Test_Parse_GFF(s_sample_GFF)
    if mod :
        Test_Out_GFF(mod)
    
