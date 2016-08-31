# auto generate code, LiuTaoTao

from lib import *

class GnoFrac_Module:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_Module(self)


class GnoFrac_funcdef:
    def __init__(self, n, v2, v3, v4, vq):
        self.n = n
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.vq = vq

    def walkabout(self, visitor):
        return visitor.visit_funcdef(self)


class GnoFrac_init_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_init_blk(self)


class GnoFrac_loop_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_loop_blk(self)


class GnoFrac_bailout_blk:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_bailout_blk(self)


class GnoFrac_default_blk:
    def __init__(self, vlst):
        self.vlst = vlst

    def walkabout(self, visitor):
        return visitor.visit_default_blk(self)


class GnoFrac_float_param:
    def __init__(self, n, v):
        self.n = n
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_float_param(self)


class GnoFrac_complex_param:
    def __init__(self, n, v2, v3):
        self.n = n
        self.v2 = v2
        self.v3 = v3

    def walkabout(self, visitor):
        return visitor.visit_complex_param(self)


class GnoFrac_float_func:
    def __init__(self, n1, n2):
        self.n1 = n1
        self.n2 = n2

    def walkabout(self, visitor):
        return visitor.visit_float_func(self)


class GnoFrac_assign:
    def __init__(self, n, v):
        self.n = n
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_assign(self)


class GnoFrac_Number:
    def __init__(self, f):
        self.f = f

    def walkabout(self, visitor):
        return visitor.visit_Number(self)


class GnoFrac_NegNumber:
    def __init__(self, f):
        self.f = f

    def walkabout(self, visitor):
        return visitor.visit_NegNumber(self)


class GnoFrac_value:
    def __init__(self, v1, s, v3):
        self.v1 = v1
        self.s = s
        self.v3 = v3

    def walkabout(self, visitor):
        return visitor.visit_value(self)


class GnoFrac_EnclosedValue:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_EnclosedValue(self)


class GnoFrac_AbsSigned:
    def __init__(self, v):
        self.v = v

    def walkabout(self, visitor):
        return visitor.visit_AbsSigned(self)


class GnoFrac_funccall:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def walkabout(self, visitor):
        return visitor.visit_funccall(self)


class GnoFrac_Name0:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name0(self)


class GnoFrac_Name1:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name1(self)


class GnoFrac_Name2:
    def __init__(self, n):
        self.n = n

    def walkabout(self, visitor):
        return visitor.visit_Name2(self)

class GnoFrac_sample_visitor_00:
    def visit_Module(self, node): pass
    def visit_funcdef(self, node): pass
    def visit_init_blk(self, node): pass
    def visit_loop_blk(self, node): pass
    def visit_bailout_blk(self, node): pass
    def visit_default_blk(self, node): pass
    def visit_float_param(self, node): pass
    def visit_complex_param(self, node): pass
    def visit_float_func(self, node): pass
    def visit_assign(self, node): pass
    def visit_Number(self, node): pass
    def visit_NegNumber(self, node): pass
    def visit_value(self, node): pass
    def visit_EnclosedValue(self, node): pass
    def visit_AbsSigned(self, node): pass
    def visit_funccall(self, node): pass
    def visit_Name0(self, node): pass
    def visit_Name1(self, node): pass
    def visit_Name2(self, node): pass

class GnoFrac_sample_visitor_01:
    def visit_Module(self, node):
        node.v.walkabout(self)
    def visit_funcdef(self, node):
        node.v2.walkabout(self)
        node.v3.walkabout(self)
        node.v4.walkabout(self)
        if node.vq is not None:
            node.vq.walkabout(self)
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
    def visit_float_param(self, node):
        node.v.walkabout(self)
    def visit_complex_param(self, node):
        node.v2.walkabout(self)
        node.v3.walkabout(self)
    def visit_float_func(self, node):
        pass
    def visit_assign(self, node):
        node.v.walkabout(self)
    def visit_Number(self, node):
        pass
    def visit_NegNumber(self, node):
        pass
    def visit_value(self, node):
        node.v1.walkabout(self)
        node.v3.walkabout(self)
    def visit_EnclosedValue(self, node):
        node.v.walkabout(self)
    def visit_AbsSigned(self, node):
        node.v.walkabout(self)
    def visit_funccall(self, node):
        node.v1.walkabout(self)
        node.v2.walkabout(self)
    def visit_Name0(self, node):
        pass
    def visit_Name1(self, node):
        pass
    def visit_Name2(self, node):
        pass

class GnoFrac_out_visitor_01:
    def __init__(self, outp):
        self.outp = outp
    def visit_Module(self, node):
        node.v.walkabout(self)
    def visit_funcdef(self, node):
        self.outp.puts(node.n)
        self.outp.puts('{')
        self.outp.newline()
        node.v2.walkabout(self)
        self.outp.newline()
        node.v3.walkabout(self)
        self.outp.newline()
        node.v4.walkabout(self)
        self.outp.newline()
        if node.vq is not None:
            node.vq.walkabout(self)
        self.outp.newline()
        self.outp.puts('}')
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
    def visit_float_param(self, node):
        self.outp.puts('float param')
        self.outp.puts(node.n)
        self.outp.newline()
        self.outp.puts('default =')
        node.v.walkabout(self)
        self.outp.newline()
        self.outp.puts('endparam')
    def visit_complex_param(self, node):
        self.outp.puts('complex param')
        self.outp.puts(node.n)
        self.outp.newline()
        self.outp.puts('default = (')
        node.v2.walkabout(self)
        self.outp.puts(',')
        node.v3.walkabout(self)
        self.outp.puts(')')
        self.outp.newline()
        self.outp.puts('endparam')
    def visit_float_func(self, node):
        self.outp.puts('float func')
        self.outp.puts(node.n1)
        self.outp.newline()
        self.outp.puts('default =')
        self.outp.puts(node.n2)
        self.outp.newline()
        self.outp.puts('endfunc')
    def visit_assign(self, node):
        self.outp.puts(node.n)
        self.outp.puts('=')
        node.v.walkabout(self)
    def visit_Number(self, node):
        self.outp.puts(node.f)
    def visit_NegNumber(self, node):
        self.outp.puts('-')
        self.outp.lnk()
        self.outp.puts(node.f)
    def visit_value(self, node):
        node.v1.walkabout(self)
        self.outp.putss(node.s)
        node.v3.walkabout(self)
    def visit_EnclosedValue(self, node):
        self.outp.puts('(')
        node.v.walkabout(self)
        self.outp.puts(')')
    def visit_AbsSigned(self, node):
        self.outp.puts('|')
        node.v.walkabout(self)
        self.outp.puts('|')
    def visit_funccall(self, node):
        node.v1.walkabout(self)
        self.outp.puts('(')
        node.v2.walkabout(self)
        self.outp.puts(')')
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
            IgnoreCls(' \t\n', [';.*']),
        ]
        self.lex_NUMBER_DOUBLE = HowRe(r'\d+\.\d+')
    
    def handle_NUMBER_DOUBLE(self):
        return self.handle_Lex(self.lex_NUMBER_DOUBLE)

    def handle_Module(self):
        self.Skip(0)
        sav0 = self.getpos()
        v = self.handle_funcdef()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_ENDMARKER() is None:
            self.setpos(sav0)
            return None
        return GnoFrac_Module(v)

    def handle_funcdef(self):
        sav0 = self.getpos()
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('{') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_init_blk()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v3 = self.handle_loop_blk()
        if v3 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v4 = self.handle_bailout_blk()
        if v4 is None:
            self.setpos(sav0)
            return None
        sav1 = self.getpos()
        self.Skip(0)
        vq = self.handle_default_blk()
        if vq is None:
            self.setpos(sav1)
        self.Skip(0)
        if self.handle_OpChar('}') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_funcdef(n, v2, v3, v4, vq)

    def handle_init_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('init:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GnoFrac_init_blk(vlst)

    def handle_loop_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('loop:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        vlst = []
        sav1 = self.getpos()
        while True:
            v3 = self.hdl_stmt()
            if v3 is None:
                break
            vlst.append(v3)
            sav1 = self.getpos()
            self.Skip(0)
        self.setpos(sav1)
        return GnoFrac_loop_blk(vlst)

    def handle_bailout_blk(self):
        sav0 = self.getpos()
        if self.handle_OpChar('bailout:') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_value()
        if v is None:
            self.setpos(sav0)
            return None
        return GnoFrac_bailout_blk(v)

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
        return GnoFrac_default_blk(vlst)

    def hdl_def_item(self):
        v = self.handle_float_param()
        if v is not None:
            return v
        v = self.handle_complex_param()
        if v is not None:
            return v
        return self.handle_float_func()

    def handle_float_param(self):
        sav0 = self.getpos()
        if self.handle_NAME('float') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('param') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('default') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.hdl_Number00()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('endparam') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_float_param(n, v)

    def handle_complex_param(self):
        sav0 = self.getpos()
        if self.handle_NAME('complex') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('param') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('default') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.hdl_Number00()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(',') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v3 = self.hdl_Number00()
        if v3 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('endparam') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_complex_param(n, v2, v3)

    def handle_float_func(self):
        sav0 = self.getpos()
        if self.handle_NAME('float') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('func') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n1 = self.handle_NAME()
        if n1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('default') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        n2 = self.handle_NAME()
        if n2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_NAME('endfunc') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_float_func(n1, n2)

    def hdl_stmt(self):
        return self.handle_assign()

    def handle_assign(self):
        sav0 = self.getpos()
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('=') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_value()
        if v is None:
            self.setpos(sav0)
            return None
        return GnoFrac_assign(n, v)

    def handle_Number(self):
        sav0 = self.getpos()
        f = self.handle_NUMBER_DOUBLE()
        if f is None:
            self.setpos(sav0)
            return None
        return GnoFrac_Number(f)

    def handle_NegNumber(self):
        sav0 = self.getpos()
        if self.handle_OpChar('-') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        f = self.handle_NUMBER_DOUBLE()
        if f is None:
            self.setpos(sav0)
            return None
        return GnoFrac_NegNumber(f)

    def hdl_Number00(self):
        v = self.handle_Number()
        if v is not None:
            return v
        return self.handle_NegNumber()

    def hdl_value0(self):
        v = self.handle_Name1()
        if v is not None:
            return v
        v = self.handle_Name2()
        if v is not None:
            return v
        v = self.handle_Name0()
        if v is not None:
            return v
        return self.hdl_Number00()

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

    def handle_value(self):
        v = self.hdl_value1()
        if v is None:
            return None
        return self.step3_value(v)
    
    def step1_value(self, v1):
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
        v1 = GnoFrac_value(v1, op, v2)
        return self.step1_value(v1)
    
    def step2_value(self, v1):
        v1 = self.step1_value(v1)
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
        v2 = self.step1_value(v2)
        v1 = GnoFrac_value(v1, op, v2)
        return self.step2_value(v1)
    
    def step3_value(self, v1):
        v1 = self.step2_value(v1)
        sav0 = self.getpos()
        self.Skip(0)
        op = self.GetOpInLst(['>', '<'])
        if op is None:
            self.setpos(sav0)
            return v1
        self.Skip(0)
        v2 = self.hdl_value1()
        if v2 is None:
            self.setpos(sav0)
            return v1
        v2 = self.step2_value(v2)
        v1 = GnoFrac_value(v1, op, v2)
        return self.step3_value(v1)

    def handle_EnclosedValue(self):
        sav0 = self.getpos()
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_value()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_EnclosedValue(v)

    def handle_AbsSigned(self):
        sav0 = self.getpos()
        if self.handle_OpChar('|') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v = self.handle_value()
        if v is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('|') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_AbsSigned(v)

    def handle_funccall(self):
        sav0 = self.getpos()
        v1 = self.hdl_value0()
        if v1 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar('(') is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        v2 = self.handle_value()
        if v2 is None:
            self.setpos(sav0)
            return None
        self.Skip(0)
        if self.handle_OpChar(')') is None:
            self.setpos(sav0)
            return None
        return GnoFrac_funccall(v1, v2)

    def handle_Name0(self):
        sav0 = self.getpos()
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GnoFrac_Name0(n)

    def handle_Name1(self):
        sav0 = self.getpos()
        if self.handle_OpChar('#') is None:
            self.setpos(sav0)
            return None
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GnoFrac_Name1(n)

    def handle_Name2(self):
        sav0 = self.getpos()
        if self.handle_OpChar('@') is None:
            self.setpos(sav0)
            return None
        n = self.handle_NAME()
        if n is None:
            self.setpos(sav0)
            return None
        return GnoFrac_Name2(n)

def Test_Parse_GnoFrac(srctxt):
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


def Test_Out_GnoFrac(mod):
    outp = OutPrt()
    the = GnoFrac_out_visitor_01(outp)
    mod.walkabout(the)
    outp.newline()

s_sample_GnoFrac = '''

Mandelbrot {
init:
    z = #zwpixel
loop:
    z = z * z + #pixel
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
    mod = Test_Parse_GnoFrac(s_sample_GnoFrac)
    if mod :
        Test_Out_GnoFrac(mod)
    
