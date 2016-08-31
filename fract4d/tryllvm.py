import numpy as np
from numba import njit
from ctypes import CFUNCTYPE, c_int, c_long, c_double, c_void_p
import llvmlite.binding as llvm

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU. The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine

def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    return mod

class OneModule:
    def __init__(self, ir_src):
        llvm_ir = """
            ; ModuleID = "examples/ir_fpadd.py"
            target triple = "unknown-unknown-unknown"
            target datalayout = ""
            define double @"fpadd"(double %".1", double %".2")
            {
            entry:
            %"res" = fadd double %".1", %".2"
            ret double %"res"
            }
            """
        llvm_ir = ir_src

        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter() # yes, even this one
        self.engine = create_execution_engine()

        compile_ir(self.engine, llvm_ir)

    def GetFuncPtr(self, func_name):
        func_ptr = self.engine.get_function_address(func_name)
        return func_ptr

src_Mandelbrot_1 = '''
target datalayout = ""
target triple = "x86_64-apple-darwin15.0.0"

define i32 @"__main__.Mandelbrot_1$4.float64.complex128.complex128.int64"(
    { i64, i64, { double, double } }* noalias nocapture %retptr,
    ;{ i8*, i32 }** noalias nocapture readnone %excinfo,
    ;i8* noalias nocapture readnone %env,
    double %arg.fbailout,
    double %arg.pixel.0,
    double %arg.pixel.1,
    double %arg.zwpixel.0,
    double %arg.zwpixel.1,
    i64 %arg.maxiter) #0 {
entry:
  br label %B27

B27:                                              ; preds = %entry, %B81
  %t__h_numiter.0 = phi i64 [ 0, %entry ], [ %.218, %B81 ]
  %z.sroa.14.0 = phi double [ %arg.zwpixel.1, %entry ], [ %.112, %B81 ]
  %z.sroa.0.0 = phi double [ %arg.zwpixel.0, %entry ], [ %.109, %B81 ]
  %.77 = fmul double %z.sroa.0.0, %z.sroa.0.0
  %.78 = fmul double %z.sroa.14.0, %z.sroa.14.0
  %.79 = fmul double %z.sroa.14.0, %z.sroa.0.0
  %.81 = fsub double %.77, %.78
  %.84 = fadd double %.79, %.79
  %.109 = fadd double %.81, %arg.pixel.0
  %.112 = fadd double %.84, %arg.pixel.1
  %.146 = fmul double %.109, %.109
  %.174 = fmul double %.112, %.112
  %.184 = fadd double %.146, %.174
  %.194 = fcmp ult double %.184, %arg.fbailout
  br i1 %.194, label %B81, label %B117

B81:                                              ; preds = %B27
  %.218 = add nuw nsw i64 %t__h_numiter.0, 1
  %.231 = icmp slt i64 %.218, %arg.maxiter
  br i1 %.231, label %B27, label %B117

B117:                                             ; preds = %B27, %B81
  %t__h_numiter.1 = phi i64 [ %.218, %B81 ], [ %t__h_numiter.0, %B27 ]
  %t__h_inside.0 = phi i64 [ 1, %B81 ], [ 0, %B27 ]
  %.265 = insertvalue { i64, i64, { double, double } } undef, i64 %t__h_inside.0, 0
  %.266 = insertvalue { i64, i64, { double, double } } %.265, i64 %t__h_numiter.1, 1
  %0 = insertvalue { double, double } undef, double %.109, 0
  %extracted.f2 = insertvalue { double, double } %0, double %.112, 1
  %.288 = insertvalue { i64, i64, { double, double } } %.266, { double, double } %extracted.f2, 2
  store { i64, i64, { double, double } } %.288, { i64, i64, { double, double } }* %retptr, align 8
  ret i32 0
}

define i32 @"LiudMandelbrot"({i64, i64, double, double}* %"retp", double %"pixel.0", double %"pixel.1", double %"zwpixel.0", double %"zwpixel.1", i64 %"maxiter")
{
entry:
  br label %"body"
body:
  %"z.0" = phi double [%"zwpixel.0", %"entry"], [%"z.0.2", %"label1"]
  %"z.1" = phi double [%"zwpixel.1", %"entry"], [%"z.1.2", %"label1"]
  %"numiter" = phi i64 [0, %"entry"], [%".22", %"label1"]
  %".9" = fmul double %"z.0", %"z.0"
  %".10" = fmul double %"z.1", %"z.1"
  %".11" = fsub double %".9", %".10"
  %".12" = fmul double %"z.0", %"z.1"
  %".13" = fmul double %"z.1", %"z.0"
  %".14" = fadd double %".12", %".13"
  %".15" = fadd double %".11", %"pixel.0"
  %".16" = fadd double %".14", %"pixel.1"
  %".17" = fmul double %".15", %".15"
  %".18" = fmul double %".16", %".16"
  %".19" = fadd double %".17", %".18"
  %".20" = fcmp ult double %".19", 0x4010000000000000
  br i1 %".20", label %"label1", label %"exit"
label1:
  %"z.0.2" = phi double [%".15", %"body"]
  %"z.1.2" = phi double [%".16", %"body"]
  %"numiter.2" = phi i64 [%"numiter", %"body"]
  %".22" = add i64 %"numiter.2", 1
  %".23" = icmp sge i64 %".22", %"maxiter"
  br i1 %".23", label %"exit", label %"body"
exit:
  %"z.0.1" = phi double [%".15", %"body"], [%"z.0.2", %"label1"]
  %"z.1.1" = phi double [%".16", %"body"], [%"z.1.2", %"label1"]
  %"inside" = phi i64 [0, %"body"], [1, %"label1"]
  %"numiter.1" = phi i64 [%"numiter", %"body"], [%".22", %"label1"]
  %".25" = insertvalue {i64, i64, double, double} undef, i64 %"inside", 0
  %".26" = insertvalue {i64, i64, double, double} %".25", i64 %"numiter.1", 1
  %".27" = insertvalue {i64, i64, double, double} %".26", double %"z.0.1", 2
  %".28" = insertvalue {i64, i64, double, double} %".27", double %"z.1.1", 3
  store {i64, i64, double, double} %".28", {i64, i64, double, double}* %"retp"
  ret i32 0
}

define i32 @"__main__.CGNewton3_1$5.complex128.complex128.int64"(
    { i64, i64, { double, double } }* noalias nocapture %retptr,
    ; { i8*, i32 }** noalias nocapture %excinfo,
    ; i8* noalias nocapture readnone %env,
    double %arg.p1.0,
    double %arg.p1.1,
    double %arg.pixel.0,
    double %arg.pixel.1,
    i64 %arg.maxiter) #0 {
entry:
  br label %B36

B36:                                              ; preds = %entry, %B128
  %t__h_numiter.0 = phi i64 [ 0, %entry ], [ %.433, %B128 ]
  %z.sroa.12.0 = phi double [ 1.000000e+00, %entry ], [ %.320, %B128 ]
  %z.sroa.0.0 = phi double [ 1.000000e+00, %entry ], [ %.317, %B128 ]
  %.100 = fmul double %z.sroa.0.0, %z.sroa.0.0
  %.101 = fmul double %z.sroa.12.0, %z.sroa.12.0
  %.102 = fmul double %z.sroa.12.0, %z.sroa.0.0
  %.104 = fsub double %.100, %.101
  %.107 = fadd double %.102, %.102
  %.138 = fmul double %z.sroa.0.0, %.104
  %.139 = fmul double %z.sroa.12.0, %.107
  %.140 = fmul double %z.sroa.0.0, %.107
  %.141 = fmul double %z.sroa.12.0, %.104
  %.142 = fsub double %.138, %.139
  %.145 = fadd double %.140, %.141
  %.176 = fsub double %.142, %arg.pixel.0
  %.179 = fsub double %.145, %arg.pixel.1
  %.212 = fmul double %.176, %arg.p1.0
  %.213 = fmul double %.179, %arg.p1.1
  %.214 = fmul double %.179, %arg.p1.0
  %.215 = fmul double %.176, %arg.p1.1
  %.216 = fsub double %.212, %.213
  %.219 = fadd double %.214, %.215
  %.254 = fmul double %.104, 3.000000e+00
  %.255 = fmul double %.107, 0.000000e+00
  %.256 = fmul double %.104, 0.000000e+00
  %.257 = fmul double %.107, 3.000000e+00
  %.258 = fsub double %.254, %.255
  %.261 = fadd double %.256, %.257
  %.78.not.i = fcmp oeq double %.258, 0.000000e+00
  %.89.i = fcmp oeq double %.261, 0.000000e+00
  %or.cond.i = and i1 %.78.not.i, %.89.i
  br i1 %or.cond.i, label %B36.if, label %B65.i

B65.i:                                            ; preds = %B36
  %.130.i = tail call double @llvm.fabs.f64(double %.258) #0
  %.140.i = tail call double @llvm.fabs.f64(double %.261) #0
  %.148.i = fcmp ult double %.130.i, %.140.i
  br i1 %.148.i, label %B169.i, label %B89.i

B89.i:                                            ; preds = %B65.i
  %0 = fcmp une double %.258, 0.000000e+00
  br i1 %0, label %B108.endif.i, label %B36.endif

B169.i:                                           ; preds = %B65.i
  %.350.i = fcmp une double %.261, 0.000000e+00
  br i1 %.350.i, label %B188.endif.i, label %B36.endif

B108.endif.i:                                     ; preds = %B89.i
  %.217.i = fdiv double %.261, %.258
  %.229.i = fmul double %.261, %.217.i
  %.237.i = fadd double %.258, %.229.i
  %.270.i = fcmp oeq double %.237.i, 0.000000e+00
  br i1 %.270.i, label %B36.if, label %B108.endif.endif.endif.i, !prof !0

B108.endif.endif.endif.i:                         ; preds = %B108.endif.i
  %.282.i = fmul double %.216, %.217.i
  %.292.i = fsub double %.219, %.282.i
  %.256.i = fmul double %.219, %.217.i
  %.262.i = fadd double %.216, %.256.i
  %.274.i = fdiv double %.262.i, %.237.i
  %.306.i = fdiv double %.292.i, %.237.i
  br label %B36.endif

B188.endif.i:                                     ; preds = %B169.i
  %.402.i = fdiv double %.258, %.261
  %.413.i = fmul double %.258, %.402.i
  %.421.i = fadd double %.261, %.413.i
  %.475.i = fcmp oeq double %.421.i, 0.000000e+00
  br i1 %.475.i, label %B36.if, label %B188.endif.endif.endif.i, !prof !0

B188.endif.endif.endif.i:                         ; preds = %B188.endif.i
  %.496.i = fmul double %.219, %.402.i
  %.517.i = fsub double %.496.i, %.216
  %.448.i = fmul double %.216, %.402.i
  %.465.i = fadd double %.219, %.448.i
  %.479.i = fdiv double %.465.i, %.421.i
  %.531.i = fdiv double %.517.i, %.421.i
  br label %B36.endif

B128:                                             ; preds = %B36.endif
  %.433 = add nuw nsw i64 %t__h_numiter.0, 1
  %.446 = icmp slt i64 %.433, %arg.maxiter
  br i1 %.446, label %B36, label %B164

B164:                                             ; preds = %B36.endif, %B128
  %t__h_numiter.1 = phi i64 [ %.433, %B128 ], [ %t__h_numiter.0, %B36.endif ]
  %t__h_inside.0 = phi i64 [ 1, %B128 ], [ 0, %B36.endif ]
  %.480 = insertvalue { i64, i64, { double, double } } undef, i64 %t__h_inside.0, 0
  %.481 = insertvalue { i64, i64, { double, double } } %.480, i64 %t__h_numiter.1, 1
  %1 = insertvalue { double, double } undef, double %.317, 0
  %extracted.f2 = insertvalue { double, double } %1, double %.320, 1
  %.503 = insertvalue { i64, i64, { double, double } } %.481, { double, double } %extracted.f2, 2
  store { i64, i64, { double, double } } %.503, { i64, i64, { double, double } }* %retptr, align 8
  ret i32 0

B36.if:                                           ; preds = %B36, %B108.endif.i, %B188.endif.i
  ;%excinfo.1.sroa.0.1 = phi i64 [ ptrtoint ({ i8*, i32 }* @.const.picklebuf.4379875448 to i64), %B36 ], [ ptrtoint ({ i8*, i32 }* @.const.picklebuf.4379876240 to i64), %B108.endif.i ], [ ptrtoint ({ i8*, i32 }* @.const.picklebuf.4379876240 to i64), %B188.endif.i ]
  ;%2 = bitcast { i8*, i32 }** %excinfo to i64*
  ;store i64 %excinfo.1.sroa.0.1, i64* %2, align 8
  ret i32 1

B36.endif:                                        ; preds = %B108.endif.endif.endif.i, %B188.endif.endif.endif.i, %B89.i, %B169.i
  %.274.sroa.6.0.ph = phi double [ 0x7FF8000000000000, %B169.i ], [ 0x7FF8000000000000, %B89.i ], [ %.306.i, %B108.endif.endif.endif.i ], [ %.531.i, %B188.endif.endif.endif.i ]
  %.274.sroa.0.0.ph = phi double [ 0x7FF8000000000000, %B169.i ], [ 0x7FF8000000000000, %B89.i ], [ %.274.i, %B108.endif.endif.endif.i ], [ %.479.i, %B188.endif.endif.endif.i ]
  %.317 = fsub double %z.sroa.0.0, %.274.sroa.0.0.ph
  %.320 = fsub double %z.sroa.12.0, %.274.sroa.6.0.ph
  %.354 = fmul double %.176, %.176
  %.384 = fmul double %.179, %.179
  %.394 = fadd double %.354, %.384
  %.407 = fcmp ugt double %.394, 1.000000e-04
  br i1 %.407, label %B128, label %B164
}

declare double @llvm.fabs.f64(double) #1

!0 = !{!"branch_weights", i32 1, i32 99}

define i32 @"CGNewton3"({i64, i64, double, double}* %"retp", double %"pixel.0", double %"pixel.1", double %"zwpixel.0", double %"zwpixel.1", i64 %"maxiter")
{
entry:
  br label %"body"
body:
  %"z.0" = phi double [0x3ff0000000000000, %"entry"], [%"z.0.2", %"label1"]
  %"z.1" = phi double [0x3ff0000000000000, %"entry"], [%"z.1.2", %"label1"]
  %"numiter" = phi i64 [0, %"entry"], [%".52", %"label1"]
  %".9" = fmul double %"z.0", %"z.0"
  %".10" = fmul double %"z.1", %"z.1"
  %".11" = fsub double %".9", %".10"
  %".12" = fmul double %"z.0", %"z.1"
  %".13" = fmul double %"z.1", %"z.0"
  %".14" = fadd double %".12", %".13"
  %".15" = fmul double %"z.0", %".11"
  %".16" = fmul double %"z.1", %".14"
  %".17" = fsub double %".15", %".16"
  %".18" = fmul double %"z.0", %".14"
  %".19" = fmul double %"z.1", %".11"
  %".20" = fadd double %".18", %".19"
  %".21" = fsub double %".17", %"pixel.0"
  %".22" = fsub double %".20", %"pixel.1"
  %".23" = fmul double 0x3fe53375da1ab247, %".21"
  %".24" = fmul double 0xbfcc7736615c9a2a, %".22"
  %".25" = fsub double %".23", %".24"
  %".26" = fmul double 0x3fe53375da1ab247, %".22"
  %".27" = fmul double 0xbfcc7736615c9a2a, %".21"
  %".28" = fadd double %".26", %".27"
  %".29" = fmul double %".11", 0x4008000000000000
  %".30" = fmul double %".14", 0x4008000000000000
  %".31" = fsub double 0x0, %".30"
  %".32" = fmul double %".25", %".29"
  %".33" = fmul double %".28", %".31"
  %".34" = fsub double %".32", %".33"
  %".35" = fmul double %".25", %".31"
  %".36" = fmul double %".28", %".29"
  %".37" = fadd double %".35", %".36"
  %".38" = fmul double %".29", %".29"
  %".39" = fmul double %".30", %".30"
  %".40" = fadd double %".38", %".39"
  %".41" = fdiv double %".34", %".40"
  %".42" = fdiv double %".37", %".40"
  %".43" = fsub double %"z.0", %".41"
  %".44" = fsub double %"z.1", %".42"
  %".45" = fsub double %".17", %"pixel.0"
  %".46" = fsub double %".20", %"pixel.1"
  %".47" = fmul double %".45", %".45"
  %".48" = fmul double %".46", %".46"
  %".49" = fadd double %".47", %".48"
  %".50" = fcmp ult double 0x3f1a36e2eb1c432d, %".49"
  br i1 %".50", label %"label1", label %"exit"
label1:
  %"z.0.2" = phi double [%".43", %"body"]
  %"z.1.2" = phi double [%".44", %"body"]
  %"numiter.2" = phi i64 [%"numiter", %"body"]
  %".52" = add i64 %"numiter.2", 1
  %".53" = icmp sge i64 %".52", %"maxiter"
  br i1 %".53", label %"exit", label %"body"
exit:
  %"z.0.1" = phi double [%".43", %"body"], [%"z.0.2", %"label1"]
  %"z.1.1" = phi double [%".44", %"body"], [%"z.1.2", %"label1"]
  %"inside" = phi i64 [0, %"body"], [1, %"label1"]
  %"numiter.1" = phi i64 [%"numiter", %"body"], [%".52", %"label1"]
  %".55" = insertvalue {i64, i64, double, double} undef, i64 %"inside", 0
  %".56" = insertvalue {i64, i64, double, double} %".55", i64 %"numiter.1", 1
  %".57" = insertvalue {i64, i64, double, double} %".56", double %"z.0.1", 2
  %".58" = insertvalue {i64, i64, double, double} %".57", double %"z.1.1", 3
  store {i64, i64, double, double} %".58", {i64, i64, double, double}* %"retp"
  ret i32 0
}

define i32 @"__main__.Cubic_Mandelbrot_1$7.complex128.float64.complex128.complex128.int64"(
    { i64, i64, { double, double } }* noalias nocapture %retptr,
    ; { i8*, i32 }** noalias nocapture readnone %excinfo,
    ; i8* noalias nocapture readnone %env,
    double %arg.fa.0,
    double %arg.fa.1,
    double %arg.fbailout,
    double %arg.pixel.0,
    double %arg.pixel.1,
    double %arg.zwpixel.0,
    double %arg.zwpixel.1,
    i64 %arg.maxiter) #0 {
entry:
  %.124 = fmul double %arg.fa.0, 3.000000e+00
  %.125 = fmul double %arg.fa.1, 0.000000e+00
  %.126 = fmul double %arg.fa.0, 0.000000e+00
  %.127 = fmul double %arg.fa.1, 3.000000e+00
  %.128 = fsub double %.124, %.125
  %.131 = fadd double %.126, %.127
  br label %B27

B27:                                              ; preds = %entry, %B75
  %t__h_numiter.0 = phi i64 [ 0, %entry ], [ %.294, %B75 ]
  %z.sroa.12.0 = phi double [ %arg.zwpixel.1, %entry ], [ %.227, %B75 ]
  %z.sroa.0.0 = phi double [ %arg.zwpixel.0, %entry ], [ %.224, %B75 ]
  %.82 = fmul double %z.sroa.0.0, %z.sroa.0.0
  %.83 = fmul double %z.sroa.12.0, %z.sroa.12.0
  %.84 = fmul double %z.sroa.12.0, %z.sroa.0.0
  %.86 = fsub double %.82, %.83
  %.89 = fadd double %.84, %.84
  %.158 = fsub double %z.sroa.0.0, %.128
  %.161 = fsub double %z.sroa.12.0, %.131
  %.188 = fmul double %.158, %.86
  %.189 = fmul double %.161, %.89
  %.190 = fmul double %.161, %.86
  %.191 = fmul double %.158, %.89
  %.192 = fsub double %.188, %.189
  %.195 = fadd double %.190, %.191
  %.224 = fadd double %.192, %arg.pixel.0
  %.227 = fadd double %.195, %arg.pixel.1
  %.30.i = fmul double %.227, %.227
  %.60.i = fmul double %.224, %.224
  %.70.i = fadd double %.60.i, %.30.i
  %.268 = fcmp ult double %.70.i, %arg.fbailout
  br i1 %.268, label %B75, label %B111

B75:                                              ; preds = %B27
  %.294 = add nuw nsw i64 %t__h_numiter.0, 1
  %.307 = icmp slt i64 %.294, %arg.maxiter
  br i1 %.307, label %B27, label %B111

B111:                                             ; preds = %B27, %B75
  %t__h_numiter.1 = phi i64 [ %.294, %B75 ], [ %t__h_numiter.0, %B27 ]
  %t__h_inside.0 = phi i64 [ 1, %B75 ], [ 0, %B27 ]
  %.345 = insertvalue { i64, i64, { double, double } } undef, i64 %t__h_inside.0, 0
  %.346 = insertvalue { i64, i64, { double, double } } %.345, i64 %t__h_numiter.1, 1
  %0 = insertvalue { double, double } undef, double %.224, 0
  %extracted.f2 = insertvalue { double, double } %0, double %.227, 1
  %.368 = insertvalue { i64, i64, { double, double } } %.346, { double, double } %extracted.f2, 2
  store { i64, i64, { double, double } } %.368, { i64, i64, { double, double } }* %retptr, align 8
  ret i32 0
}

define i32 @"CubicMandelbrot"({i64, i64, double, double}* %"retp", double %"pixel.0", double %"pixel.1", double %"zwpixel.0", double %"zwpixel.1", i64 %"maxiter")
{
entry:
  br label %"body"
body:
  %"z.0" = phi double [%"zwpixel.0", %"entry"], [%"z.0.2", %"label1"]
  %"z.1" = phi double [%"zwpixel.1", %"entry"], [%"z.1.2", %"label1"]
  %"numiter" = phi i64 [0, %"entry"], [%".32", %"label1"]
  %".9" = fmul double %"z.0", %"z.0"
  %".10" = fmul double %"z.1", %"z.1"
  %".11" = fsub double %".9", %".10"
  %".12" = fmul double %"z.0", %"z.1"
  %".13" = fmul double %"z.1", %"z.0"
  %".14" = fadd double %".12", %".13"
  %".15" = fmul double              0x0, 0x4008000000000000
  %".16" = fmul double              0x0, 0x4008000000000000
  %".17" = fsub double %"z.0", %".15"
  %".18" = fsub double %"z.1", %".16"
  %".19" = fmul double %".11", %".17"
  %".20" = fmul double %".14", %".18"
  %".21" = fsub double %".19", %".20"
  %".22" = fmul double %".11", %".18"
  %".23" = fmul double %".14", %".17"
  %".24" = fadd double %".22", %".23"
  %".25" = fadd double %".21", %"pixel.0"
  %".26" = fadd double %".24", %"pixel.1"
  %".27" = fmul double %".25", %".25"
  %".28" = fmul double %".26", %".26"
  %".29" = fadd double %".27", %".28"
  %".30" = fcmp ult double %".29", 0x4010000000000000
  br i1 %".30", label %"label1", label %"exit"
label1:
  %"z.0.2" = phi double [%".25", %"body"]
  %"z.1.2" = phi double [%".26", %"body"]
  %"numiter.2" = phi i64 [%"numiter", %"body"]
  %".32" = add i64 %"numiter.2", 1
  %".33" = icmp sge i64 %".32", %"maxiter"
  br i1 %".33", label %"exit", label %"body"
exit:
  %"z.0.1" = phi double [%".25", %"body"], [%"z.0.2", %"label1"]
  %"z.1.1" = phi double [%".26", %"body"], [%"z.1.2", %"label1"]
  %"inside" = phi i64 [0, %"body"], [1, %"label1"]
  %"numiter.1" = phi i64 [%"numiter", %"body"], [%".32", %"label1"]
  %".35" = insertvalue {i64, i64, double, double} undef, i64 %"inside", 0
  %".36" = insertvalue {i64, i64, double, double} %".35", i64 %"numiter.1", 1
  %".37" = insertvalue {i64, i64, double, double} %".36", double %"z.0.1", 2
  %".38" = insertvalue {i64, i64, double, double} %".37", double %"z.1.1", 3
  store {i64, i64, double, double} %".38", {i64, i64, double, double}* %"retp"
  ret i32 0
}

'''

g_Module = OneModule(src_Mandelbrot_1)

LiudMandelbrot_ptr = g_Module.GetFuncPtr("LiudMandelbrot")
cfunc2_LiudMandelbrot = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(LiudMandelbrot_ptr)

CubicMandelbrot_ptr = g_Module.GetFuncPtr('CubicMandelbrot')
cfunc2_CubicMandelbrot = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(CubicMandelbrot_ptr)

CGNewton3_ptr = g_Module.GetFuncPtr('CGNewton3')
cfunc2_CGNewton3 = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(CGNewton3_ptr)

Mandelbrot_1_ptr = g_Module.GetFuncPtr("__main__.Mandelbrot_1$4.float64.complex128.complex128.int64")
cfunc2_Mandelbrot_1 = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_double, c_long)(Mandelbrot_1_ptr)

CGNewton3_1_ptr = g_Module.GetFuncPtr('__main__.CGNewton3_1$5.complex128.complex128.int64')
cfunc2_CGNewton3_1 = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_long)(CGNewton3_1_ptr)

Cubic_Mandelbrot_1_ptr = g_Module.GetFuncPtr('__main__.Cubic_Mandelbrot_1$7.complex128.float64.complex128.complex128.int64')
cfunc2_Cubic_Mandelbrot_1 = CFUNCTYPE(c_int, c_void_p, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_long)(Cubic_Mandelbrot_1_ptr)


dtype_i8i8f8f8 = np.dtype([('i1', 'i8'),('i2', 'i8'),('i3', 'f8'),('i4', 'f8')])
#dtype_i8i8f8f8 = np.dtype([('foo', np.int64),('foo1', np.int64),('bar1', np.float64),('bar', np.float64)])

@njit
def test33():
    t__a_fbailout, pixel, zwpixel, maxiter = 4.0, (-0.805474821772-0.180754042393j), 0j, 2008
    #arr = np.array([(0,0,0,0)], dtype=dtype_i8i8f8f8)
    arr = np.zeros(1, dtype=dtype_i8i8f8f8)
    print cfunc2_Mandelbrot_1(arr.ctypes.data, t__a_fbailout, pixel.real, pixel.imag, zwpixel.real, zwpixel.imag, maxiter)
    a1,a2,a3,a4 = arr[0]['i1'], arr[0]['i2'], arr[0]['i3'], arr[0]['i4']
    a1 = a1 + len(arr) - len(arr)
    return a1,a2,a3,a4


if __name__ == '__main__':
    a1,a2,a3,a4 = test33()

    print 'test:', a1,a2,a3,a4

    t__a_fbailout, pixel, zwpixel, maxiter = 4.0, (-0.805474821772-0.180754042393j), 0j, 2008

    import mycalc
    print mycalc.Mandelbrot_1(t__a_fbailout, pixel, zwpixel, maxiter)
