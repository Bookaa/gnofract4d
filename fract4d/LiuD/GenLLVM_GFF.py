import Ast_GFF
from Ast_GFF import GFF_sample_visitor_01, Test_Parse_GFF, s_sample_GFF
from ParseFormFile import getdt

import llvmlite.ir as ir
import llvmlite.binding as llvm

from ctypes import CFUNCTYPE, c_int, c_long, c_double, c_void_p
import math

g_tolerance = True

type_int = 1
type_double = 2
type_complex = 3
type_bool = 4
type_enum_string = 5

def getLocalVars(dict_):
    keys = []
    for kname in dict_:
        val = dict_[kname]
        if isinstance(val, tuple) and len(val) == 2:
            keys.append(kname)
    return keys

class mywalk(GFF_sample_visitor_01):
    def init(self, mod0, mod1, mod2, param0, param1, param2):
        module = ir.Module()

        self.module = module
        self.funcprotos = {}
        self.vardict = {'_keys_':set()}
        self.temno = 0

        self.mod0 = mod0
        self.mod1 = mod1
        self.mod2 = mod2
        self.param0 = param0
        self.param1 = param1
        self.param2 = param2
        self.dict1 = {'_keys_':set()}
        self.dict2 = {'_keys_':set()}
        self.color0 = (self.vardict, self.param0, self.mod0)
        self.color1 = (self.dict1, self.param1, self.mod1)
        self.color2 = (self.dict2, self.param2, self.mod2)
        self.cur_color = self.color0

        self.globalfuncs = {}

    def new_phi(self, typ, kname):
        if typ == type_double:
            return self.irbuilder.phi(ir.DoubleType(), kname)
        if typ == type_int:
            return self.irbuilder.phi(ir.IntType(64), kname)
        if typ == type_complex:
            v1 = self.irbuilder.phi(ir.DoubleType(), kname+'_real')
            v2 = self.irbuilder.phi(ir.DoubleType(), kname+'_imag')
            return (v1, v2)
        assert False

    def InitColorInOut(self, color):
        dict_, param, mod = color
        for v in mod.vlst:
            if isinstance(v, Ast_GFF.GFF_init_blk):
                break
        else:
            return
        self.cur_color = color
        for v1 in v.vlst:
            v1.walkabout(self)
        self.cur_color = self.color0

    def ColorInOut_EntryToLoop(self, color, cur_entry):
        dict_, param, mod = color
        keys = dict_.keys()
        if not keys:
            return
        dic_loop = {}
        for kname in keys:
            if kname == '_keys_':
                continue    # temperoly
            typ, val = dict_[kname]
            v = self.new_phi(typ, kname)
            if typ == type_complex:
                v[0].add_incoming(val[0], cur_entry)
                v[1].add_incoming(val[1], cur_entry)
            else:
                v.add_incoming(val, cur_entry)
            dict_[kname] = typ, v
            dic_loop[kname] = v
        dict_['loop'] = dic_loop

    def ColorInOut_LoopToExit(self, color, cur_entry):
        dict_, param, mod = color
        keys = getLocalVars(dict_)
        if not keys:
            return
        dic_exit = {}
        for kname in keys:
            typ, val = dict_[kname]
            v = self.new_phi(typ, kname)
            if typ == type_complex:
                v[0].add_incoming(val[0], cur_entry)
                v[1].add_incoming(val[1], cur_entry)
            else:
                v.add_incoming(val, cur_entry)
            dic_exit[kname] = v
        dict_['exit'] = dic_exit

    def ColorInOut_Loop(self, color):
        dict_, param, mod = color
        for v in mod.vlst:
            if isinstance(v, Ast_GFF.GFF_loop_blk):
                break
        else:
            return
        self.cur_color = color
        for v1 in v.vlst:
            v1.walkabout(self)
        self.cur_color = self.color0

    def visit_if_stmt(self, node):
        if_to_lst = [(node.v1, node.v2)]
        for v in node.vlst:
            if_to_lst.append((v.v1, v.v2))
        if node.vq:
            if_to_lst.append((None, node.vq))
        return self.visit_if(if_to_lst)
    def visit_if(self, if_to_lst):
        if len(if_to_lst) > 1:
            return self.visit_if2(if_to_lst)
        v1, v2 = if_to_lst[0]
        condi = v1.walkabout(self)

        cur_entry = self.irbuilder.block

        label_if = self.irbuilder.append_basic_block("label_if")
        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi[1], label_if, label_endif)

        self.irbuilder.position_at_end(label_if)

        dict_, _, _ = self.cur_color
        sav_set = dict_['_keys_']; dict_['_keys_'] = set()

        theb = class_branch(label_endif, dict_)

        theb.add_jumppoint(cur_entry, dict_)

        # if body
        v2.walkabout(self)

        if_entry = self.irbuilder.block
        theb.add_jumppoint(if_entry, dict_)
        theb.restore_dict(dict_)
        with self.irbuilder.goto_block(theb.label):
            theb.add_incomings(dict_, self.new_phi)
        dict_['_keys_'] = theb.leave(dict_, sav_set)

        self.irbuilder.branch(label_endif)
        self.irbuilder.position_at_end(label_endif)
    def visit_if2(self, if_to_lst):
        v1, v2 = if_to_lst.pop(0)
        condi = v1.walkabout(self)

        label_if = self.irbuilder.append_basic_block("label_if")
        label_else = self.irbuilder.append_basic_block("label_else")
        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi[1], label_if, label_else)

        dict_, _, _ = self.cur_color
        sav2 = dict_.copy()
        theb = class_branch(label_endif, dict_)
        sav_set = dict_['_keys_']; dict_['_keys_'] = set()


        self.irbuilder.position_at_end(label_if)

        # if body
        v2.walkabout(self)
        if_entry = self.irbuilder.block
        theb.add_jumppoint(if_entry, dict_)

        self.irbuilder.branch(label_endif)

        theb.restore_dict(dict_)
        #dict_ = sav2.copy()
        self.irbuilder.position_at_end(label_else)
        dict_['_keys_'] = set()

        # else body
        if if_to_lst[0][0] is not None:
            self.visit_if(if_to_lst)
        else:
            v = if_to_lst[0][1]
            v.walkabout(self)

        else_entry = self.irbuilder.block
        theb.add_jumppoint(else_entry, dict_)
        theb.restore_dict(dict_)
        #dict_ = sav2
        with self.irbuilder.goto_block(theb.label):
            theb.add_incomings(dict_, self.new_phi)
        dict_['_keys_'] = theb.leave(dict_, sav_set)

        self.irbuilder.branch(label_endif)

        self.irbuilder.position_at_end(label_endif)

    def ColorInOut_Label1ToExit(self, color, cur_entry):
        dict_, param, mod = color
        if 'exit' not in dict_:
            return
        dic = dict_['exit']
        for kname in dic:
            typ,val = dict_[kname]
            if typ == type_complex:
                dic[kname][0].add_incoming(val[0], cur_entry)
                dic[kname][1].add_incoming(val[1], cur_entry)
            else:
                dic[kname].add_incoming(val, cur_entry)

    def ColorInOut_Label1ToLoop(self, color, cur_entry):
        dict_, param, mod = color
        if 'loop' not in dict_:
            return
        dic = dict_['loop']
        for kname in dic:
            typ,val = dict_[kname]
            if typ == type_complex:
                dic[kname][0].add_incoming(val[0], cur_entry)
                dic[kname][1].add_incoming(val[1], cur_entry)
            else:
                dic[kname].add_incoming(val, cur_entry)

    def DeepIn_default(self, mod):
        sav = self.default_blk
        for v in mod.vlst:
            if isinstance(v, Ast_GFF.GFF_default_blk):
                self.default_blk = v
                break
        return sav
    def ColorInOut_final(self, color, label_endifblk):
        dict_, param, mod = color
        for v in mod.vlst:
            if isinstance(v, Ast_GFF.GFF_final_blk):
                break
        else:
            return
        name = mod.n.strip()

        if True:
            dict_['index'] = type_double, ir.Constant(ir.DoubleType(), 0.0)
            dict_['solid'] = type_int, ir.Constant(ir.IntType(64), 0)
            self.cur_color = color
            savdb = self.DeepIn_default(mod)
            for v1 in v.vlst:
                v1.walkabout(self)
            self.default_blk = savdb
            self.cur_color = self.color0

            cur_entry = self.irbuilder.block
            with self.irbuilder.goto_block(label_endifblk):     # to endif
                if '_final_endif_' not in self.vardict:
                    pass
                for kname, v in self.vardict['_final_endif_'].items():
                    v.add_incoming(dict_[kname][1], cur_entry)
                    self.vardict[kname] = type_double, v


    def do_tolerence(self):
        '''
        if t__h_numiter >= min_period_iter:
            if (t__h_numiter & save_mask) == 0:
                old_z = z
                save_incr -= 1
                if save_incr == 0:
                    save_mask = (save_mask << 1) + 1
                    save_incr = next_save_incr
            else:
                if math.fabs(z.real - old_z.real) < period_tolerance and math.fabs(z.imag - old_z.imag) < period_tolerance:
                    t__h_inside = 1
                    break
        '''
        if not g_tolerance:
            return
        v_numiter = Ast_GFF.GFF_Name0('numiter')
        v_mpi = Ast_GFF.GFF_Name0('min_period_iter')
        v_condi = Ast_GFF.GFF_value2(v_numiter, '>=', v_mpi)
        condi = v_condi.walkabout(self)

        # below code copy from visit_if

        cur_entry = self.irbuilder.block

        label_if = self.irbuilder.append_basic_block("label_if")
        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi[1], label_if, label_endif)

        self.irbuilder.position_at_end(label_if)

        dict_, _, _ = self.cur_color
        keys = ['old_z', 'save_incr', 'save_mask']
        sav_val = {kname : dict_[kname][1] for kname in keys}

        # if body
        #v2.walkabout(self)
        self.do_tolerence2()

        if_entry = self.irbuilder.block
        with self.irbuilder.goto_block(label_endif):     # to label_endif
            for kname in keys:
                typ, val = dict_[kname]
                val2 = sav_val[kname]
                v = self.new_phi(typ, kname)
                if typ == type_complex:
                    v[0].add_incoming(val[0], if_entry)
                    v[1].add_incoming(val[1], if_entry)
                    v[0].add_incoming(val2[0], cur_entry)
                    v[1].add_incoming(val2[1], cur_entry)
                else:
                    v.add_incoming(val, if_entry)
                    v.add_incoming(val2, cur_entry)
                dict_[kname] = typ, v

        self.irbuilder.branch(label_endif)
        self.irbuilder.position_at_end(label_endif)

    def do_tolerence2(self):
        '''
            if (t__h_numiter & save_mask) == 0:
                old_z = z
                save_incr -= 1
                if save_incr == 0:
                    save_mask = (save_mask << 1) + 1
                    save_incr = next_save_incr
            else:
                if math.fabs(z.real - old_z.real) < period_tolerance and math.fabs(z.imag - old_z.imag) < period_tolerance:
                    t__h_inside = 1
                    break
        '''
        v_numiter = Ast_GFF.GFF_Name0('numiter')
        v_smk = Ast_GFF.GFF_Name0('save_mask')
        typ1,val1 = v_numiter.walkabout(self)
        typ2,val2 = v_smk.walkabout(self)
        val3 = self.irbuilder.and_(val1, val2)
        zero = ir.Constant(ir.IntType(64), 0)
        condi = self.irbuilder.icmp_signed('==', val3, zero)
        # below code copy from visit_if2
        label_if = self.irbuilder.append_basic_block("label_if")
        label_else = self.irbuilder.append_basic_block("label_else")
        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi, label_if, label_else)

        dict_, _, _ = self.cur_color
        keys = ['old_z', 'save_incr', 'save_mask']
        savall = dict_.copy()

        self.irbuilder.position_at_end(label_if)

        # if body
        #v2.walkabout(self)
        self.do_tolerence3()
        endif_dict = {}
        if_entry = self.irbuilder.block
        with self.irbuilder.goto_block(label_endif):     # to label_endif
            for kname in keys:
                typ, val = dict_[kname]
                v = self.new_phi(typ, kname)
                if typ == type_complex:
                    v[0].add_incoming(val[0], if_entry)
                    v[1].add_incoming(val[1], if_entry)
                else:
                    v.add_incoming(val, if_entry)
                endif_dict[kname] = v

        self.irbuilder.branch(label_endif)
        self.irbuilder.position_at_end(label_else)

        for key,val in savall.items():
            dict_[key] = val
        # else body
        self.do_tolerence4()

        else_entry = self.irbuilder.block
        with self.irbuilder.goto_block(label_endif):     # to label_endif
            for kname in keys:
                typ, val = dict_[kname]
                v = endif_dict[kname]
                if typ == type_complex:
                    v[0].add_incoming(val[0], else_entry)
                    v[1].add_incoming(val[1], else_entry)
                else:
                    v.add_incoming(val, else_entry)
                dict_[kname] = typ, v
        self.irbuilder.branch(label_endif)

        self.irbuilder.position_at_end(label_endif)
    def do_tolerence3(self):
        '''
        old_z = z
        save_incr -= 1
        if save_incr == 0:
            save_mask = (save_mask << 1) + 1
            save_incr = next_save_incr
        '''
        zero = ir.Constant(ir.IntType(64), 0)
        one = ir.Constant(ir.IntType(64), 1)
        self.vardict['old_z'] = self.vardict['z']
        self.vardict['save_incr'] = type_int, self.irbuilder.sub(self.vardict['save_incr'][1], one)

        condi = self.irbuilder.icmp_signed('==', self.vardict['save_incr'][1], zero)
        # below copy from visit_if
        cur_entry = self.irbuilder.block

        label_if = self.irbuilder.append_basic_block("label_if")
        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi, label_if, label_endif)

        self.irbuilder.position_at_end(label_if)

        dict_, _, _ = self.cur_color
        keys = ['save_incr', 'save_mask']
        sav_val = {kname : dict_[kname][1] for kname in keys}

        # if body
        #v2.walkabout(self)
        if True:
            '''
            save_mask = (save_mask << 1) + 1
            save_incr = next_save_incr
            '''
            typ, val = self.vardict['save_mask']
            val1 = self.irbuilder.shl(val, one)
            val2 = self.irbuilder.add(val1, one)
            self.vardict['save_mask'] = typ, val2
            self.vardict['save_incr'] = self.vardict['next_save_incr']

        if_entry = self.irbuilder.block
        with self.irbuilder.goto_block(label_endif):     # to label_endif
            for kname in keys:
                typ, val = dict_[kname]
                val2 = sav_val[kname]
                v = self.new_phi(typ, kname)
                if typ == type_complex:
                    v[0].add_incoming(val[0], if_entry)
                    v[1].add_incoming(val[1], if_entry)
                    v[0].add_incoming(val2[0], cur_entry)
                    v[1].add_incoming(val2[1], cur_entry)
                else:
                    v.add_incoming(val, if_entry)
                    v.add_incoming(val2, cur_entry)
                dict_[kname] = typ, v

        self.irbuilder.branch(label_endif)
        self.irbuilder.position_at_end(label_endif)

    def do_tolerence4(self):
        '''
        if math.fabs(z.real - old_z.real) < period_tolerance and math.fabs(z.imag - old_z.imag) < period_tolerance:
            t__h_inside = 1
            break
        '''
        typ1, (z_real, z_imag) = self.vardict['z']
        typ2, (oz_real, oz_imag) = self.vardict['old_z']
        val1 = self.irbuilder.fsub(z_real, oz_real)
        val2 = self.irbuilder.fsub(z_imag, oz_imag)
        funcname = 'fabs'
        func_p = self.globalfuncs.get(funcname)
        if not func_p:
            func_t = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ])
            func_p = ir.Function(self.module, func_t, funcname)
            self.globalfuncs[funcname] = func_p

        val3 = self.irbuilder.call(func_p, (val1,))
        val4 = self.irbuilder.call(func_p, (val2,))
        typ3, val_tol = self.vardict['period_tolerance']
        condi1 = self.irbuilder.fcmp_ordered('<', val3, val_tol)
        condi2 = self.irbuilder.fcmp_ordered('<', val4, val_tol)
        condi = type_int, self.irbuilder.and_(condi1, condi2)
        one = ir.Constant(ir.IntType(64), 1)
        # -----

        label_endif = self.irbuilder.append_basic_block("label_endif")

        self.irbuilder.cbranch(condi[1], self.loop_exit, label_endif)

        # if body
        if True:
            '''
            t__h_inside = 1
            break
            '''

        cur_entry = self.irbuilder.block
        with self.irbuilder.goto_block(self.loop_exit):     # to loop_exit
            self.vardict['_exit_']['inside'].add_incoming(one, cur_entry)
            self.vardict['_exit_']['numiter'].add_incoming(self.vardict['numiter'][1], cur_entry)
            self.vardict['_exit_']['z'][0].add_incoming(self.vardict['z'][1][0], cur_entry)
            self.vardict['_exit_']['z'][1].add_incoming(self.vardict['z'][1][1], cur_entry)

            self.ColorInOut_Label1ToExit(self.color1, cur_entry)
            self.ColorInOut_Label1ToExit(self.color2, cur_entry)

        self.irbuilder.position_at_end(label_endif)

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

        zero = ir.Constant(ir.IntType(64), 0)

        self.vardict['pixel'] = (type_complex, (func.args[1], func.args[2]))
        self.vardict['zwpixel'] = (type_complex, (func.args[3], func.args[4]))
        self.vardict['maxiter'] = (type_int, func.args[5])
        self.vardict['fate'] = type_int, zero
        self.vardict['numiter'] = type_int, zero

        if g_tolerance:
            self.vardict['min_period_iter'] = (type_int, ir.Constant(ir.IntType(64), 10))
            self.vardict['period_tolerance'] = (type_double, ir.Constant(ir.DoubleType(), 0.0001))
            self.vardict['save_mask'] = (type_int, ir.Constant(ir.IntType(64), 9))
            self.vardict['save_incr'] = (type_int, ir.Constant(ir.IntType(64), 1))
            self.vardict['next_save_incr'] = (type_int, ir.Constant(ir.IntType(64), 4))

        # entry point of func
        bb_entry = func.append_basic_block('entry')
        self.irbuilder = ir.IRBuilder(bb_entry)

        init_blk.walkabout(self)
        if g_tolerance:
            self.vardict['old_z'] = self.vardict['z']

        self.InitColorInOut(self.color1)
        self.InitColorInOut(self.color2)

        loop_blk.walkabout(self)
        bailout_blk.walkabout(self)

        self.do_final()

        value_indx = self.vardict['index']
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
            self.vardict['index'] = (type_double, ir.Constant(ir.DoubleType(), 0.000000001))
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

        if True:
            with self.irbuilder.goto_block(label_endifblk):
                self.vardict['_final_endif_'] = {'index' : self.new_phi(type_double, 'index'),
                       'solid' : self.new_phi(type_int, 'solid')}

        savall = self.vardict.copy()

        # in ifblk
        self.ColorInOut_final(self.color1, label_endifblk)

        self.irbuilder.branch(label_endifblk)

        self.vardict = savall

        self.irbuilder.position_at_end(label_elseblk)
        #else_entry = self.irbuilder.block

        self.ColorInOut_final(self.color2, label_endifblk)

        self.irbuilder.branch(label_endifblk)

        self.irbuilder.position_at_end(label_endifblk)

        '''
        init:
        float angle = #pi

        loop:
            temp_angle = abs(atan2(z))
            if temp_angle < angle
                angle = temp_angle
            endif

        final:
            #index = angle/#pi
        '''
    def visit_loop_blk(self, node):
        # now is entry
        self.loop_body = self.irbuilder.append_basic_block("body")
        self.loop_exit = self.irbuilder.append_basic_block("exit")

        self.irbuilder.branch(self.loop_body)

        key = ['z', 'numiter']
        if g_tolerance:
            key.extend(['old_z', 'save_incr', 'save_mask'])

        dict_ = {}
        entry1 = self.irbuilder.block
        with self.irbuilder.goto_block(self.loop_body):     # entry to body
            for kname in key:
                typ, val = self.vardict[kname]
                v = self.new_phi(typ, kname)
                if typ == type_complex:
                    v[0].add_incoming(val[0], entry1)
                    v[1].add_incoming(val[1], entry1)
                else:
                    v.add_incoming(val, entry1)
                self.vardict[kname] = typ, v
                dict_[kname] = v
            self.vardict['_loop_'] = dict_

            self.ColorInOut_EntryToLoop(self.color1, entry1)
            self.ColorInOut_EntryToLoop(self.color2, entry1)

        # now is body

        self.irbuilder.position_at_end(self.loop_body)

        for v in node.vlst:
            v.walkabout(self)

    def visit_bailout_blk(self, node):
        # now is body
        entry2 = self.irbuilder.block

        typ, val = node.v.walkabout(self)
        cond = val
        self_label1 = self.irbuilder.append_basic_block("label1")
        self.irbuilder.cbranch(cond, self_label1, self.loop_exit)

        dict_exit = {}
        with self.irbuilder.goto_block(self.loop_exit): # body -> exit
            val1,val2 = self.vardict['z'][1]
            loop_z0_body, loop_z1_body = self.new_phi(type_complex, 'z')
            loop_z0_body.add_incoming(val1, entry2)
            loop_z1_body.add_incoming(val2, entry2)
            dict_exit['z'] = (loop_z0_body, loop_z1_body)

            value_inside = self.new_phi(type_int, "inside")
            value_inside.add_incoming(ir.Constant(ir.IntType(64), 0), entry2)
            dict_exit['inside'] = value_inside

            value_numiter = self.new_phi(type_int, "numiter")
            value_numiter.add_incoming(self.vardict['numiter'][1], entry2)
            dict_exit['numiter'] = value_numiter

            self.vardict['_exit_'] = dict_exit

            self.ColorInOut_LoopToExit(self.color1, entry2)
            self.ColorInOut_LoopToExit(self.color2, entry2)

        # now is label 1
        self.irbuilder.position_at_end(self_label1)
        self.do_tolerence()
        self.ColorInOut_Loop(self.color1)
        self.ColorInOut_Loop(self.color2)

        self.vardict['_keys_'].add('numiter')
        self.vardict['numiter'] = type_int, self.irbuilder.add(self.vardict['numiter'][1], ir.Constant(ir.IntType(64), 1))

        entry3 = self.irbuilder.block
        value_comp = self.irbuilder.icmp_signed('>=', self.vardict['numiter'][1], self.vardict['maxiter'][1])
        self.irbuilder.cbranch(value_comp, self.loop_exit, self.loop_body)

        with self.irbuilder.goto_block(self.loop_exit): # label1 -> exit
            self.vardict['_exit_']['z'][0].add_incoming(self.vardict['z'][1][0], entry3)
            self.vardict['_exit_']['z'][1].add_incoming(self.vardict['z'][1][1], entry3)
            self.vardict['_exit_']['inside'].add_incoming(ir.Constant(ir.IntType(64), 1), entry3)
            self.vardict['_exit_']['numiter'].add_incoming(self.vardict['numiter'][1], entry3)

            self.ColorInOut_Label1ToExit(self.color1, entry3)
            self.ColorInOut_Label1ToExit(self.color2, entry3)

        with self.irbuilder.goto_block(self.loop_body):    # label1 -> body
            for kname,v in self.vardict['_loop_'].items():
                typ, val = self.vardict[kname]
                if typ == type_complex:
                    v[0].add_incoming(val[0], entry3)
                    v[1].add_incoming(val[1], entry3)
                else:
                    v.add_incoming(val, entry3)

            self.ColorInOut_Label1ToLoop(self.color1, entry3)
            self.ColorInOut_Label1ToLoop(self.color2, entry3)

        # now is exit

        self.irbuilder.position_at_end(self.loop_exit)
        self.vardict['inside'] = type_int, self.vardict['_exit_']['inside']
        self.vardict['numiter'] = type_int, self.vardict['_exit_']['numiter']
        self.vardict['z'] = type_complex, self.vardict['_exit_']['z']

    def visit_declare(self, node):
        dt = getdt(node.v1.s)
        if isinstance(node.v2, Ast_GFF.GFF_Name0):
            name = node.v2.n
        elif isinstance(node.v2, Ast_GFF.GFF_Name1):
            name = node.v2.n
        else:
            assert False
        dict_, _, _ = self.cur_color
        if dt == 1:
            typ, val = type_int, ir.Constant(ir.IntType(64), 0)
        elif dt == 2:
            typ, val = type_double, ir.Constant(ir.DoubleType(), 0.0)
        else:
            assert False
        dict_[name] = typ, val

    def visit_assign(self, node):
        #assign : AssignDT? nameq+ value
        #    nameq : (Name0|Name1) '='

        typ_val = node.v.walkabout(self)
        if typ_val is None:
            typ_val = node.v.walkabout(self)
        typ, val = typ_val
        def sub_func1():
            if len(node.vlst) == 1:
                dest = node.vlst[0]
                dict_, _, _ = self.cur_color
                if isinstance(dest, Ast_GFF.GFF_nameq) and isinstance(dest.v, Ast_GFF.GFF_Name0):
                    destname = dest.v.n
                    if destname in dict_:
                        dict_['_keys_'].add(destname)
                    dict_[destname] = typ, val
                    return
                if isinstance(dest, Ast_GFF.GFF_nameq) and isinstance(dest.v, Ast_GFF.GFF_Name1):
                    destname = dest.v.n
                    if destname in dict_:
                        dict_['_keys_'].add(destname)
                    dict_[destname] = typ, val
                    return
            assert False

        if node.vq is None:
            return sub_func1()
        dt = getdt(node.vq.s)
        if dt == 1 and typ == type_int:
            return sub_func1()
        if dt == 2 and typ == type_double:
            return sub_func1()
        if dt == 3 and typ == type_complex:
            return sub_func1()
        assert False
    def visit_Name0(self, node):
        dict_, _, _ = self.cur_color
        name = node.n
        return dict_.get(name, None) or self.vardict[name]
    def visit_Name1(self, node):
        dict_, _, _ = self.cur_color
        name = node.n
        if name == 'pi':
            return type_double, ir.Constant(ir.DoubleType(), math.pi)
        return dict_.get(name, None) or self.vardict[name]
    def visit_Name2(self, node):
        name = node.n
        typ, val = self.get_param_value(name)
        return typ, val
    def visit_Number(self, node):
        return type_double, ir.Constant(ir.DoubleType(), float(node.f))
    def visit_Numi(self, node):
        return type_int, ir.Constant(ir.IntType(64), int(node.i))
    def visit_bool_value(self, node):
        if node.s == 'true':
            return type_int, ir.Constant(ir.IntType(64), 1)
        return type_int, ir.Constant(ir.IntType(64), 0)

    def visit_Num_Complex(self, node):
        typ1, v_real = node.v1.walkabout(self)
        typ2, v_imag = node.v2.walkabout(self)
        if typ1 == type_int:
            v_real = self.irbuilder.sitofp(v_real, ir.DoubleType())
        if typ2 == type_int:
            v_imag = self.irbuilder.sitofp(v_imag, ir.DoubleType())
        return type_complex, (v_real, v_imag)

    def visit_value2(self, node):
        typ1, val1 = node.v1.walkabout(self)
        if node.s == '==' and typ1 == type_enum_string:
            assert isinstance(node.v3, Ast_GFF.GFF_String)
            v3_str = node.v3.s[0]
            if val1[1] == v3_str:
                # now is True
                return type_bool, ir.Constant(ir.IntType(1), 1)
            return type_bool, ir.Constant(ir.IntType(1), 0)
        typ2_val2 = node.v3.walkabout(self)
        if typ2_val2 is None:
            typ2_val2 = node.v3.walkabout(self)
        typ2, val2 = typ2_val2
        if node.s == '*' and (typ1, typ2) == (type_double, type_complex):
            tem1 = self.irbuilder.fmul(val2[0], val1)
            tem2 = self.irbuilder.fmul(val2[1], val1)
            return type_complex, (tem1, tem2)

        if node.s == '*' and typ1 == typ2 == type_double:
            return typ1, self.irbuilder.fmul(val1, val2)
        if node.s == '*' and typ1 == typ2 == type_complex:
            val3 = self.complex_mul(val1, val2)
            return typ1, val3
        if node.s == '*' and (typ1, typ2) == (type_int, type_double):
            todouble = self.irbuilder.sitofp(val1, ir.DoubleType())
            return typ2, self.irbuilder.fmul(todouble, val2)

        if node.s == '/' and typ1 == typ2 == type_complex:
            val3 = self.complex_div(val1, val2)
            return typ1, val3
        if node.s == '/' and typ1 == typ2 == type_double:
            return typ1, self.irbuilder.fdiv(val1, val2)
        if node.s == '/' and (typ1, typ2) == (type_int, type_double):
            todouble = self.irbuilder.sitofp(val1, ir.DoubleType())
            return typ2, self.irbuilder.fdiv(todouble, val2)
        if node.s == '/' and (typ1, typ2) == (type_double, type_int):
            todouble = self.irbuilder.sitofp(val2, ir.DoubleType())
            return typ1, self.irbuilder.fdiv(val1, todouble)

        if node.s == '+' and typ1 == typ2 == type_complex:
            #print 'complex add'
            tem1 = self.irbuilder.fadd(val1[0], val2[0])
            tem2 = self.irbuilder.fadd(val1[1], val2[1])
            return typ1, (tem1, tem2)
        if node.s == '+' and (typ1, typ2) == (type_double, type_int):
            todouble = self.irbuilder.sitofp(val2, ir.DoubleType())
            return typ1, self.irbuilder.fadd(val1, todouble)

        if node.s == '+' and typ1 == typ2 == type_double:
            return typ1, self.irbuilder.fadd(val1, val2)
        if node.s == '+' and (typ1, typ2) == (type_int, type_double):
            todouble = self.irbuilder.sitofp(val1, ir.DoubleType())
            return typ2, self.irbuilder.fadd(todouble, val2)

        if node.s == '-' and typ1 == typ2 == type_complex:
            tem1 = self.irbuilder.fsub(val1[0], val2[0])
            tem2 = self.irbuilder.fsub(val1[1], val2[1])
            return typ1, (tem1, tem2)

        if node.s in ('<','>','>=') and typ1 == typ2 == type_double:
            tem1 = self.irbuilder.fcmp_ordered(node.s, val1, val2)
            return type_int, tem1
        if node.s in ('<','>','>=') and (typ1, typ2) == (type_double, type_int):
            todouble = self.irbuilder.sitofp(val2, ir.DoubleType())
            tem1 = self.irbuilder.fcmp_ordered(node.s, val1, todouble)
            return type_int, tem1
        if node.s in ('<','>','>=') and typ1 == typ2 == type_int:
            tem1 = self.irbuilder.icmp_signed(node.s, val1, val2)
            return type_int, tem1
        if node.s == '||':
            #assert typ1 == typ2 == type_bool
            return typ1, self.irbuilder.or_(val1, val2)

        if node.s == '%' and (typ1, typ2) == (type_double, type_int):
            #toint = self.irbuilder.fptosi(val1, ir.IntType(64))
            #return typ2, self.irbuilder.srem(toint, val2)
            todouble = self.irbuilder.sitofp(val2, ir.DoubleType())
            if True:
                return typ1, self.irbuilder.frem(val1, todouble)
            funcname = 'fmod'
            func_p = self.globalfuncs.get(funcname)
            if not func_p:
                func_t = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ir.DoubleType()])
                func_p = ir.Function(self.module, func_t, funcname)
                self.globalfuncs[funcname] = func_p

            tem1 = self.irbuilder.call(func_p,(val1,todouble))
            return typ1, tem1

        print 'node.s ', node.s, typ1, typ2
        assert False
    def visit_EnclosedValue(self, node):
        return node.v.walkabout(self)
    def visit_neg_value(self, node):
        if isinstance(node.v, Ast_GFF.GFF_Number):
            return type_double, ir.Constant(ir.DoubleType(), -float(node.v.f))
        if isinstance(node.v, Ast_GFF.GFF_Numi):
            return type_int, ir.Constant(ir.IntType(64), -node.v.i)
        #node.v.walkabout(self)
        assert False
    def visit_AbsSigned(self, node):
        typ,val = node.v.walkabout(self)
        if typ == type_complex:
            tem3 = self.irbuilder.fmul(val[0], val[0])
            tem4 = self.irbuilder.fmul(val[1], val[1])
            tem5 = self.irbuilder.fadd(tem3, tem4)
            return type_double, tem5    # should I sqrt ?
        if typ == type_double:
            funcname = 'fabs'
            func_p = self.globalfuncs.get(funcname)
            if not func_p:
                func_t = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ])
                func_p = ir.Function(self.module, func_t, funcname)
                self.globalfuncs[funcname] = func_p

            tem2 = self.irbuilder.call(func_p, (val,))
            return type_double, tem2
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
        if funcname == 'atan2':
            func_p = self.globalfuncs.get(funcname)
            if not func_p:
                func_t = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ir.DoubleType()])
                func_p = ir.Function(self.module, func_t, funcname)
                self.globalfuncs[funcname] = func_p

            val1,val2 = val

            tem1 = self.irbuilder.call(func_p,(val2,val1))
            return type_double, tem1
        if funcname == 'abs':
            funcname = 'fabs'
            func_p = self.globalfuncs.get(funcname)
            if not func_p:
                func_t = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ])
                func_p = ir.Function(self.module, func_t, funcname)
                self.globalfuncs[funcname] = func_p

            tem2 = self.irbuilder.call(func_p, (val,))
            return type_double, tem2
        if funcname == 'real':
            assert typ == type_complex
            return type_double, val[0]
        if funcname == 'imag':
            assert typ == type_complex
            return type_double, val[1]

        print dir(node)
        print funcname
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
        dict_, param, mod = self.cur_color
        for name1, typ, val, enum in param:
            if name1 == name:
                if typ == 1:
                    if enum:
                        return type_enum_string, (val, enum[val])
                    return type_int, ir.Constant(ir.IntType(64), val)
                if typ == 2:
                    return type_double, ir.Constant(ir.DoubleType(), val)
                # return
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

        assert False, name
    def get_param_func_name(self, funcname):
        if funcname == 'bailfunc':
            return 'cmag'
        assert False

class class_branch:
    def __init__(self, label, dict_):
        self.label = label
        self.dict_ = dict_.copy()
        self.jumps = []
        self.newphis = {}
    def add_jumppoint(self, fromlabel, dict_):
        a1 = {}
        for kname in dict_['_keys_']:
            a1[kname] = dict_[kname]
        self.jumps.append((fromlabel, a1))

    def restore_dict(self, dict_):
        dict_.clear()
        dict_.update(self.dict_)

    def add_incomings(self, dict_, self_new_phi):
        #theb.add_incomings(dict_)
        keys = set()
        for label1, key1 in self.jumps:
            keys.update(key1.keys())

        i=0
        for label1, key1 in self.jumps:
            i+=1
            for kname in keys:
                if kname in key1:
                    typ, val = key1[kname]
                else:
                    typ, val = dict_[kname]
                if i == 1:
                    v = self_new_phi(typ, kname)
                    self.newphis[kname] = typ, v
                else:
                    typ, v = self.newphis[kname]
                if typ == type_complex:
                    v[0].add_incoming(val[0], label1)
                    v[1].add_incoming(val[1], label1)
                else:
                    v.add_incoming(val, label1)

    def leave(self, dict_, sav_set):
        for kname,v in self.newphis.items():
            dict_[kname] = v
            sav_set.add(kname)
        return sav_set

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
    def __init__(self, mod0, mod1, mod2, param0, param1, param2):
        # funcname = mod.n.strip()
        the = mywalk()
        the.init(mod0, mod1, mod2, param0, param1, param2)
        funcname = mod0.walkabout(the)
        ir_src = str(the.module)

        #print ir_src
        engine = llvm_func(ir_src)
        func_addr = engine.get_function_address(funcname)

        self.engine = engine
        cfuncptr = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(func_addr)
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