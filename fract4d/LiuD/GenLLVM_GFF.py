import Ast_GFF
from Ast_GFF import GFF_sample_visitor_01, Test_Parse_GFF, s_sample_GFF
from ParseFormFile import getdt

import llvmlite.ir as ir
import llvmlite.binding as llvm

from ctypes import CFUNCTYPE, c_int, c_long, c_double, c_void_p

type_double = 2
type_complex = 3
type_int = 1

class mywalk(GFF_sample_visitor_01):
    def init(self, mod1, mod2):
        module = ir.Module()

        self.module = module
        self.funcprotos = {}
        self.vardict = {}
        self.temno = 0

        self.mod1 = mod1
        self.mod2 = mod2

    def visit_formu_deep(self, node):
        funcname = node.n.strip().replace(' ','_')
        init_blk = None
        loop_blk = None
        bailout_blk = None
        self.default_blk = None
        for v in node.vlst:
            if isinstance(v, Ast_GFF.GFF_init_blk):
                init_blk = v
                continue
            if isinstance(v, Ast_GFF.GFF_loop_blk):
                loop_blk = v
                continue
            if isinstance(v, Ast_GFF.GFF_bailout_blk):
                bailout_blk = v
                continue
            if isinstance(v, Ast_GFF.GFF_default_blk):
                self.default_blk = v
                continue
            if isinstance(v, Ast_GFF.GFF_anotherfmt):
                init_blk = Ast_GFF.GFF_init_blk(v.v1.vlst)
                loop_blk = Ast_GFF.GFF_loop_blk(v.v2.vlst)
                bailout_blk = Ast_GFF.GFF_bailout_blk(v.v3)
                continue
            assert False

        module = self.module

        # main (and only) function
        rettype = ir.LiteralStructType((ir.IntType(64), ir.IntType(64), ir.DoubleType(), ir.DoubleType(), ir.DoubleType(), ir.IntType(64)))

        func_t = ir.FunctionType(ir.IntType(32),
                                 [rettype.as_pointer(), ir.DoubleType(), ir.DoubleType(), ir.DoubleType(), ir.DoubleType(), ir.IntType(64)])
        func = ir.Function(module, func_t, funcname)

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

        self.do_final()

        value_indx = self.vardict['idex']
        value_solid = self.vardict['solid']

        tem1 = rettype(ir.Undefined)
        tem2 = self.irbuilder.insert_value(tem1, self.vardict['inside'][1], (0,))
        tem3 = self.irbuilder.insert_value(tem2, self.vardict['numiter'][1], (1,))
        tem4 = self.irbuilder.insert_value(tem3, self.vardict['z'][1][0], (2,))
        tem5 = self.irbuilder.insert_value(tem4, self.vardict['z'][1][1], (3,))
        tem6 = self.irbuilder.insert_value(tem5, value_indx[1], (4,))
        tem7 = self.irbuilder.insert_value(tem6, value_solid[1], (5,))

        self.irbuilder.store(tem7, func.args[0])
        self.irbuilder.ret(ir.Constant(ir.IntType(32), 0))

        return funcname

    def do_final(self):
        if False:
            self.vardict['solid'] = (type_int, ir.Constant(ir.IntType(64), 0))
            self.vardict['idex'] = (type_double, ir.Constant(ir.DoubleType(), 0.000000001))
            return
        # solid = 0
        # if t__h_inside == 0:
        zero = ir.Constant(ir.IntType(64), 0)
        val_inside = self.vardict['inside'][1]
        condi = self.irbuilder.icmp_signed("==", val_inside, zero)

        label_ifblk = self.irbuilder.append_basic_block("if_inside")
        label_elseblk = self.irbuilder.append_basic_block("not_inside")
        label_endifblk = self.irbuilder.append_basic_block("endif")

        self.irbuilder.cbranch(condi, label_ifblk, label_elseblk)

        self.irbuilder.position_at_end(label_ifblk)
        if_entry = self.irbuilder.block

        # in ifblk
        # t__a_cf0bailout = 4.0
        # t__cf03 = abs2(z) + 0.000000001
        # t__cf06 = t__h_numiter + t__a_cf0bailout / t__cf03
        # idex = t__cf06 / 256.0
        if True:
            zero = ir.Constant(ir.IntType(64), 0)
            self.vardict['solid'] = type_int, zero

            t__a_cf0bailout = ir.Constant(ir.DoubleType(), 4.0)
            z0,z1 = self.vardict['z'][1]
            tem1 = self.irbuilder.fmul(z0, z0)
            tem2 = self.irbuilder.fmul(z1, z1)
            tem3 = self.irbuilder.fadd(tem1, tem2)
            cf03 = self.irbuilder.fadd(tem3, ir.Constant(ir.DoubleType(), 0.000000001))
            tem4 = self.irbuilder.fdiv(t__a_cf0bailout, cf03)
            todouble = self.irbuilder.sitofp(self.vardict['numiter'][1], ir.DoubleType())
            cf06 = self.irbuilder.fadd(todouble, tem4)
            idex = self.irbuilder.fdiv(cf06, ir.Constant(ir.DoubleType(), 256.0))

            with self.irbuilder.goto_block(label_endifblk):     # to endif
                endif_idex = self.irbuilder.phi(ir.DoubleType(), "idex")
                endif_idex.add_incoming(idex, if_entry)
                endif_solid = self.irbuilder.phi(ir.IntType(64), "solid")
                endif_solid.add_incoming(self.vardict['solid'][1], if_entry)

        self.irbuilder.branch(label_endifblk)

        self.irbuilder.position_at_end(label_elseblk)
        else_entry = self.irbuilder.block

        if True:
            idex = ir.Constant(ir.DoubleType(), 0.0)
            self.vardict['solid'] = type_int, ir.Constant(ir.IntType(64), 1)

            with self.irbuilder.goto_block(label_endifblk):     # to endif
                endif_idex.add_incoming(idex, else_entry)
                endif_solid.add_incoming(self.vardict['solid'][1], else_entry)

        self.vardict['solid'] = (type_int, endif_solid)
        self.vardict['idex'] = (type_double, endif_idex)

        self.irbuilder.branch(label_endifblk)

        self.irbuilder.position_at_end(label_endifblk)

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

    def visit_assign(self, node):
        #assign : AssignDT? nameq+ value
        #    nameq : (Name0|Name1) '='

        typ_val = node.v.walkabout(self)
        if typ_val is None:
            typ_val = node.v.walkabout(self)
        typ, val = typ_val

        if node.vq is None:
            if len(node.vlst) == 1:
                dest = node.vlst[0]
                if isinstance(dest, Ast_GFF.GFF_nameq) and isinstance(dest.v, Ast_GFF.GFF_Name0):
                    destname = dest.v.n
                    self.vardict[destname] = typ, val
                    return
        assert False
        if node.vq is not None:
            node.vq.walkabout(self)
        for v in node.vlst:
            v.walkabout(self)
        node.v.walkabout(self)

        # assign : NAME '=' value
        name_dest = node.n
        typ, (val1, val2) = node.v.walkabout(self)

        self.vardict[name_dest] = typ, (val1, val2)
    def visit_Name0(self, node):
        name = node.n
        return self.vardict[name]
    def visit_Name1(self, node):
        name = node.n
        return self.vardict[name]
    def visit_Name2(self, node):
        name = node.n
        typ, val = self.get_param_value(name)
        return typ, val
    def visit_Number(self, node):
        return type_double, ir.Constant(ir.DoubleType(), float(node.f))
    def visit_Numi(self, node):
        return type_int, ir.Constant(ir.IntType(64), int(node.i))
    def visit_Num_Complex(self, node):
        v_real = node.v1.walkabout(self)
        v_imag = node.v2.walkabout(self)
        return type_complex, (v_real[1], v_imag[1])

    def visit_value2(self, node):
        typ1, val1 = node.v1.walkabout(self)
        typ2_val2 = node.v3.walkabout(self)
        if typ2_val2 is None:
            typ2_val2 = node.v3.walkabout(self)
        typ2, val2 = typ2_val2
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
    def visit_EnclosedValue(self, node):
        return node.v.walkabout(self)
    def visit_neg_value(self, node):
        if isinstance(node.v, Ast_GFF.GFF_Number):
            return type_double, ir.Constant(ir.DoubleType(), -float(node.v.f))
        #node.v.walkabout(self)
        assert False
    def visit_AbsSigned(self, node):
        typ,val = node.v.walkabout(self)
        if typ == type_complex:
            tem3 = self.irbuilder.fmul(val[0], val[0])
            tem4 = self.irbuilder.fmul(val[1], val[1])
            tem5 = self.irbuilder.fadd(tem3, tem4)
            return type_double, tem5    # should I sqrt ?
        assert False
    def visit_funccall(self, node):
        #typ, val = node.v2.walkabout(self)
        if node.vq and len(node.vq.vlst) == 1:
            param1 = node.vq.vlst[0]
            typ, val = param1.walkabout(self)
        else:
            assert False
        if isinstance(node.v, Ast_GFF.GFF_Name2):
            name2 = node.v.n
            funcname = self.get_param_func_name(name2)
        else:
            funcname = node.v.n
        if funcname == 'cmag':
            tem1 = self.irbuilder.fmul(val[0], val[0])
            tem2 = self.irbuilder.fmul(val[1], val[1])
            tem3 = self.irbuilder.fadd(tem1, tem2)
            return type_double, tem3
        if funcname == 'sqr':
            if typ == type_complex:
                val3 = self.complex_mul(val, val)
                return type_complex, val3
        print dir(node)
        print node.v1.n
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
    def get_param_value(self, name):
        assert self.default_blk
        for itm in self.default_blk.vlst:
            if isinstance(itm, Ast_GFF.GFF_dt_param):
                dt = getdt(itm.v1.s)
                if isinstance(itm.v2, Ast_GFF.GFF_Name0):
                    name1 = itm.v2.n
                else:
                    assert False
                if name1 == name:
                    if dt == 2: # double
                        assert len(itm.vlst) == 1
                        assert isinstance(itm.vlst[0], Ast_GFF.GFF_df_default)
                        assert isinstance(itm.vlst[0].v, Ast_GFF.GFF_Number)
                        f = itm.vlst[0].v.f
                        return type_double, ir.Constant(ir.DoubleType(), float(f))
                    if dt == 3: # complex
                        assert len(itm.vlst) == 1
                        assert isinstance(itm.vlst[0], Ast_GFF.GFF_df_default)
                        cpx = itm.vlst[0].v
                        assert isinstance(cpx, Ast_GFF.GFF_Num_Complex)
                        value_real = cpx.v1.walkabout(self)
                        value_imag = cpx.v2.walkabout(self)
                        if value_imag is None:
                            value_imag = cpx.v2.walkabout(self)
                        return type_complex, (value_real[1], value_imag[1])
                    assert False
                continue
            elif isinstance(itm, Ast_GFF.GFF_dt_func):
                name1 = itm.n
                if name1 == name:
                    assert False
            else:
                assert False
        if False:
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
    def get_param_func_name(self, funcname):
        if funcname == 'bailfunc':
            return 'cmag'
        assert False

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
    def __init__(self, mod0, mod1, mod2):
        # funcname = mod.n.strip()
        the = mywalk()
        the.init(mod1, mod2)
        funcname = mod0.walkabout(the)
        ir_src = str(the.module)

        engine = llvm_func(ir_src)
        func_addr = engine.get_function_address(funcname)

        self.engine = engine
        cfuncptr = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(func_addr)
        self.cfuncptr = cfuncptr


if __name__ == '__main__':
    pass
