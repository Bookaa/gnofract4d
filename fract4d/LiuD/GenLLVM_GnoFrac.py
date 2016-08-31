import Ast_GnoFrac
from Ast_GnoFrac import GnoFrac_sample_visitor_01, Test_Parse_GnoFrac, s_sample_GnoFrac

import llvmlite.ir as ir
import llvmlite.binding as llvm

from ctypes import CFUNCTYPE, c_int, c_long, c_double, c_void_p

type_double = 1
type_complex = 2
type_int = 3

class mywalk(GnoFrac_sample_visitor_01):
    def init(self):
        module = ir.Module()

        self.module = module
        self.funcprotos = {}
        self.vardict = {}
        self.temno = 0

    def visit_funcdef(self, node):
        name = node.n
        init_blk = node.v2
        loop_blk = node.v3
        bailout_blk = node.v4
        self.default_blk = node.vq

        module = self.module

        # main (and only) function
        rettype = ir.LiteralStructType((ir.IntType(64), ir.IntType(64), ir.DoubleType(), ir.DoubleType()))

        func_t = ir.FunctionType(ir.IntType(32),
                                 [rettype.as_pointer(), ir.DoubleType(), ir.DoubleType(), ir.DoubleType(), ir.DoubleType(), ir.IntType(64)])
        func = ir.Function(module, func_t, name)

        func.args[0]._name = 'retp'
        func.args[1]._name = 'pixel.0'
        func.args[2]._name = 'pixel.1'
        func.args[3]._name = 'zwpixel.0'
        func.args[4]._name = 'zwpixel.1'
        func.args[5]._name = 'maxiter'

        self.vardict['pixel'] = (type_complex, (func.args[1], func.args[2]))
        self.vardict['zwpixel'] = (type_complex, (func.args[3], func.args[4]))
        self.vardict['maxiter'] = (type_int, func.args[5])

        # entry point of func
        bb_entry = func.append_basic_block('entry')
        self.irbuilder = ir.IRBuilder(bb_entry)

        init_blk.walkabout(self)
        loop_blk.walkabout(self)
        bailout_blk.walkabout(self)

        tem1 = rettype(ir.Undefined)
        tem2 = self.irbuilder.insert_value(tem1, self.vardict['inside'][1], (0,))
        tem3 = self.irbuilder.insert_value(tem2, self.vardict['numiter'][1], (1,))
        tem4 = self.irbuilder.insert_value(tem3, self.vardict['z'][1][0], (2,))
        tem5 = self.irbuilder.insert_value(tem4, self.vardict['z'][1][1], (3,))

        self.irbuilder.store(tem5, func.args[0])
        self.irbuilder.ret(ir.Constant(ir.IntType(32), 0))

    def visit_loop_blk(self, node):
        # now is entry
        loop_entry = self.irbuilder.block
        self.loop_body = self.irbuilder.append_basic_block("body")
        self.label1 = self.irbuilder.append_basic_block("label1")
        self.loop_exit = self.irbuilder.append_basic_block("exit")

        self.irbuilder.branch(self.loop_body)

        with self.irbuilder.goto_block(self.loop_body):     # entry to body
            val1,val2 = self.vardict['z'][1]
            loop_z0_body = self.irbuilder.phi(ir.DoubleType(), "z.0")
            loop_z0_body.add_incoming(val1, loop_entry)
            loop_z1_body = self.irbuilder.phi(ir.DoubleType(), "z.1")
            loop_z1_body.add_incoming(val2, loop_entry)
            self.vardict['z'] = type_complex, (loop_z0_body, loop_z1_body)

            value_numiter = self.irbuilder.phi(ir.IntType(64), "numiter")
            value_numiter.add_incoming(ir.Constant(ir.IntType(64), 0), loop_entry)
            self.vardict['numiter'] = (type_int, value_numiter)

        self.savall_body = self.vardict['z'], self.vardict['numiter']

        # now is body

        self.irbuilder.position_at_end(self.loop_body)

        for v in node.vlst:
            v.walkabout(self)

    def visit_bailout_blk(self, node):
        # now is body
        loop_entry = self.irbuilder.block

        typ, val = node.v.walkabout(self)
        cond = val
        self.irbuilder.cbranch(cond, self.label1, self.loop_exit)

        with self.irbuilder.goto_block(self.loop_exit): # body -> exit
            val1,val2 = self.vardict['z'][1]
            loop_z0_body = self.irbuilder.phi(ir.DoubleType(), "z.0")
            loop_z0_body.add_incoming(val1, loop_entry)
            loop_z1_body = self.irbuilder.phi(ir.DoubleType(), "z.1")
            loop_z1_body.add_incoming(val2, loop_entry)
            valuetuple_exit_z = type_complex, (loop_z0_body, loop_z1_body)

            value_inside = self.irbuilder.phi(ir.IntType(64), "inside")
            value_inside.add_incoming(ir.Constant(ir.IntType(64), 0), loop_entry)
            valuetuple_exit_inside = (type_int, value_inside)
            value_numiter = self.irbuilder.phi(ir.IntType(64), "numiter")
            value_numiter.add_incoming(self.vardict['numiter'][1], loop_entry)
            valuetuple_exit_numiter = (type_int, value_numiter)


        with self.irbuilder.goto_block(self.label1):    # body -> label1
            val1,val2 = self.vardict['z'][1]
            loop_z0_body = self.irbuilder.phi(ir.DoubleType(), "z.0")
            loop_z0_body.add_incoming(val1, loop_entry)
            loop_z1_body = self.irbuilder.phi(ir.DoubleType(), "z.1")
            loop_z1_body.add_incoming(val2, loop_entry)
            valuetuple_label1_z = type_complex, (loop_z0_body, loop_z1_body)

            value_numiter = self.irbuilder.phi(ir.IntType(64), "numiter")
            value_numiter.add_incoming(self.vardict['numiter'][1], loop_entry)
            valuetuple_label1_numiter = (type_int, value_numiter)

        # now is label 1
        self.irbuilder.position_at_end(self.label1)
        self.vardict['z'] = valuetuple_label1_z
        self.vardict['numiter'] = type_int, self.irbuilder.add(valuetuple_label1_numiter[1], ir.Constant(ir.IntType(64), 1))

        loop_entry = self.irbuilder.block
        value_comp = self.irbuilder.icmp_signed('>=', self.vardict['numiter'][1], self.vardict['maxiter'][1])
        self.irbuilder.cbranch(value_comp, self.loop_exit, self.loop_body)

        with self.irbuilder.goto_block(self.loop_exit): # label1 -> exit
            valuetuple_exit_z[1][0].add_incoming(self.vardict['z'][1][0], loop_entry)
            valuetuple_exit_z[1][1].add_incoming(self.vardict['z'][1][1], loop_entry)
            valuetuple_exit_inside[1].add_incoming(ir.Constant(ir.IntType(64), 1), loop_entry)
            valuetuple_exit_numiter[1].add_incoming(self.vardict['numiter'][1], loop_entry)

        with self.irbuilder.goto_block(self.loop_body):    # label1 -> body
            tuple_z, tuple_numiter = self.savall_body

            val1,val2 = self.vardict['z'][1]
            tuple_z[1][0].add_incoming(val1, loop_entry)
            tuple_z[1][1].add_incoming(val2, loop_entry)
            tuple_numiter[1].add_incoming(self.vardict['numiter'][1], loop_entry)

        # now is exit

        self.irbuilder.position_at_end(self.loop_exit)
        loop_entry = self.irbuilder.block
        self.vardict['inside'] = valuetuple_exit_inside
        self.vardict['numiter'] = valuetuple_exit_numiter
        self.vardict['z'] = valuetuple_exit_z


    def visit_default_blk(self, node): assert False
    def visit_float_param(self, node): assert False
    def visit_float_func(self, node): assert False
    def visit_assign(self, node):
        name_dest = node.n
        if isinstance(node.v, Ast_GnoFrac.GnoFrac_Name1):
            name_src = node.v.n

            typ, (val1, val2) = self.vardict[name_src]
        else:
            typ, (val1, val2) = node.v.walkabout(self)

        self.vardict[name_dest] = typ, (val1, val2)

    def visit_Number(self, node):
        return type_double, ir.Constant(ir.DoubleType(), float(node.f))
    def visit_NegNumber(self, node):
        return type_double, ir.Constant(ir.DoubleType(), -float(node.f))
    def visit_EnclosedValue(self, node):
        return node.v.walkabout(self)
    def visit_AbsSigned(self, node):
        typ,val = node.v.walkabout(self)
        if typ == type_complex:
            tem3 = self.irbuilder.fmul(val[0], val[0])
            tem4 = self.irbuilder.fmul(val[1], val[1])
            tem5 = self.irbuilder.fadd(tem3, tem4)
            return type_double, tem5    # should I sqrt ?
        assert False
    def complex_mul(self, val1, val2):
        tem1 = self.irbuilder.fmul(val1[0], val2[0])
        tem2 = self.irbuilder.fmul(val1[1], val2[1])
        tem3 = self.irbuilder.fsub(tem1, tem2)

        tem4 = self.irbuilder.fmul(val1[0], val2[1])
        tem5 = self.irbuilder.fmul(val1[1], val2[0])
        tem6 = self.irbuilder.fadd(tem4, tem5)
        return (tem3, tem6)
    def complex_div(self, val1, val2):
        neg1 = self.irbuilder.fsub(ir.Constant(ir.DoubleType(), 0.0), val2[1])
        tem1, tem2 = self.complex_mul(val1, (val2[0], neg1))
        tem3 = self.irbuilder.fmul(val2[0], val2[0])
        tem4 = self.irbuilder.fmul(val2[1], val2[1])
        tem5 = self.irbuilder.fadd(tem3, tem4)

        tem6 = self.irbuilder.fdiv(tem1, tem5)
        tem7 = self.irbuilder.fdiv(tem2, tem5)
        return (tem6, tem7)
    def visit_value(self, node):
        typ1, val1 = node.v1.walkabout(self)
        typ2, val2 = node.v3.walkabout(self)
        if node.s == '*' and (typ1, typ2) == (type_double, type_complex):
            tem1 = self.irbuilder.fmul(val2[0], val1)
            tem2 = self.irbuilder.fmul(val2[1], val1)
            return type_complex, (tem1, tem2)

        if node.s == '*' and typ1 == typ2 == type_complex:
            val3 = self.complex_mul(val1, val2)
            return typ1, val3

        if node.s == '/' and typ1 == typ2 == type_complex:
            val3 = self.complex_div(val1, val2)
            return typ1, val3

        if node.s == '+' and typ1 == typ2 == type_complex:
            #print 'complex add'
            tem1 = self.irbuilder.fadd(val1[0], val2[0])
            tem2 = self.irbuilder.fadd(val1[1], val2[1])
            return typ1, (tem1, tem2)

        if node.s == '-' and typ1 == typ2 == type_complex:
            tem1 = self.irbuilder.fsub(val1[0], val2[0])
            tem2 = self.irbuilder.fsub(val1[1], val2[1])
            return typ1, (tem1, tem2)

        if node.s == '<' and typ1 == typ2 == type_double:
            #print 'yes double compare'
            tem1 = self.irbuilder.fcmp_unordered(node.s, val1, val2)
            return type_int, tem1
        print 'node.s ', node.s, typ1, typ2
        assert False
    def visit_funccall(self, node):
        typ, val = node.v2.walkabout(self)
        if isinstance(node.v1, Ast_GnoFrac.GnoFrac_Name2):
            name2 = node.v1.n
            funcname = self.get_param_func_name(name2)
        else:
            funcname = node.v1.n
        if funcname == 'cmag':
            tem1 = self.irbuilder.fmul(val[0], val[0])
            tem2 = self.irbuilder.fmul(val[1], val[1])
            tem3 = self.irbuilder.fadd(tem1, tem2)
            return type_double, tem3
        print dir(node)
        print node.v1.n
        assert False
    def visit_Name0(self, node):
        return self.vardict[node.n]
    def visit_Name1(self, node):
        return self.vardict[node.n]
    def visit_Name2(self, node):
        name = node.n
        typ, val = self.get_param_value(name)
        return typ, val
    def NewTemVar(self, val):
        self.temno += 1
        phi = self.irbuilder.phi(ir.DoubleType(), 'tem%d' % self.temno)
        phi.add_incoming(val, self.irbuilder.block)
        return phi
    def get_param_func_name(self, funcname):
        if funcname == 'bailfunc':
            return 'cmag'
        assert False
    def get_param_value(self, name):
        assert self.default_blk
        for itm in self.default_blk.vlst:
            if isinstance(itm, Ast_GnoFrac.GnoFrac_float_param):
                if name == itm.n:
                    return type_double, ir.Constant(ir.DoubleType(), float(itm.v.f))
            if isinstance(itm, Ast_GnoFrac.GnoFrac_complex_param):
                if name == itm.n:
                    value_real = itm.v2.walkabout(self)
                    value_imag = itm.v3.walkabout(self)
                    return type_complex, (value_real[1], value_imag[1])
            if isinstance(itm, Ast_GnoFrac.GnoFrac_float_func):
                pass

        assert False


s_sample_GnoFrac_2 = '''
    CubicMandelbrot {
    ; z <- z^3 + c
    ; The cubic set actually has two critical values, but this formula just uses
    ; zero - to be fixed later.
    init:
        z = #zwpixel
        ; nothing to do here
    loop:
        z = z * z * (z - 3.0 * @a) + #pixel
    bailout:
        @bailfunc(z) < @bailout
    default:
    float param bailout
        default = 4.0
    endparam
    float func bailfunc
        default = cmag
    endfunc
    complex param a
        default = (0.0,0.0)
    endparam
    }
    '''

s_sample_GnoFrac_3 = '''
    CGNewton3 {
    init:
        z = @a
    loop:
        z2 = z * z
        z3 = z * z2
        z = z - @p1 * (z3 - #pixel) / (3.0 * z2)
    bailout:
        0.0001 < |z3 - #pixel|

    default:
    complex param a
        default = (1.0, 1.0)
    endparam
    complex param p1
        default = (0.66253178213589414, -0.22238807443609804)
    endparam
    }
    '''

def create_execution_engine(ir_src):
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = llvm.parse_assembly(ir_src)
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine

def llvm_func(ir_src):
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter() # yes, even this one
    engine = create_execution_engine(ir_src)
    #engine.add_module(module)
    engine.finalize_object()
    return engine

class LLVM_liud:
    def __init__(self, ir_src, funcname):
        mod = Test_Parse_GnoFrac(ir_src)
        if not mod :
            return
        the = mywalk()
        the.init()
        mod.walkabout(the)
        ir_src = str(the.module)

        engine = llvm_func(ir_src)
        Mandelbrot_ptr = engine.get_function_address(funcname)

        self.engine = engine
        cfuncptr = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(Mandelbrot_ptr)
        self.cfuncptr = cfuncptr



if __name__ == '__main__':
    pass


'''
entry:
    t__h_numiter = 0
    z = zwpixel
body:
    pass numiter,z
    while True:
        z = z*z + pixel
        if z.real * z.real + z.imag * z.imag >= fbailout:
            t__h_inside = 0
            break
label1:
        t__h_numiter += 1
        if t__h_numiter >= maxiter:
            t__h_inside = 1
            break
exit:
    pass numiter,inside,z
    return t__h_inside, t__h_numiter, z
'''