#!/usr/bin/env python

import unittest
import string
import sys
import fc
import os.path
import struct
import math
import types

import testbase

import gradient


pos_params = [
    0.0, 0.0, 0.0, 0.0,
    4.0,
    0.0, 0.0, 0.0, 0.0,0.0, 0.0
    ]
class Test(testbase.TestBase):
    def compileMandel(self):
        self.compiler.add_func_path('../formulas')
        self.compiler.load_formula_file("gf4d.frm")
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")
        cg = self.compiler.compile(f)
        self.compiler.generate_code(f,cg,"test-pf.so")

    def compileColorMandel(self):
        self.compiler.add_func_path('../formulas')
        self.compiler.load_formula_file("gf4d.frm")
        self.compiler.load_formula_file("gf4d.cfrm")
        cf1 = self.compiler.get_formula("gf4d.cfrm","default","cf0")
        self.assertEqual(len(cf1.errors),0)
        self.compiler.compile(cf1)
        
        cf2 = self.compiler.get_formula("gf4d.cfrm","zero","cf1")
        self.assertEqual(len(cf2.errors),0)
        self.compiler.compile(cf2)
        
        f = self.compiler.get_formula("gf4d.frm","Mandelbrot")

        self.color_mandel_params = f.symbols.default_params() + \
                                   cf1.symbols.default_params() + \
                                   cf2.symbols.default_params()

        return self.compiler.compile_all(f,cf1,cf2,[])

    def compileColorDiagonal(self):
        self.compiler.add_func_path('../formulas')
        self.compiler.load_formula_file("test.frm")
        self.compiler.load_formula_file("gf4d.cfrm")
        cf1 = self.compiler.get_formula("gf4d.cfrm","default","cf0")
        self.assertEqual(len(cf1.errors),0)

        
        cf2 = self.compiler.get_formula("gf4d.cfrm","zero","cf1")
        self.assertEqual(len(cf2.errors),0)
        self.compiler.compile(cf2)
        
        f = self.compiler.get_formula("test.frm","test_simpleshape")
        outputfile = self.compiler.compile_all(f,cf1,cf2,[])

        self.color_diagonal_params = f.symbols.default_params() + \
                                     cf1.symbols.default_params() + \
                                     cf2.symbols.default_params()

        return outputfile
    
    def setUp(self):
        compiler = fc.Compiler()
        self.compiler = compiler
        self.gradient = gradient.Gradient()
        
    def tearDown(self):
        pass


        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')


