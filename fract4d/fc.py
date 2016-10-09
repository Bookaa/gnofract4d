#!/usr/bin/env python

# A compiler from UltraFractal or Fractint formula files to C code

# The UltraFractal manual is the best current description of the file
# format. You can download it from http://www.ultrafractal.com/uf3-manual.zip

# The implementation is based on the outline in "Modern Compiler
# Implementation in ML: basic techniques" (Appel 1997, Cambridge)

# Overall structure:
# fractlexer.py and fractparser.py are the lexer and parser, respectively.
# They use the PLY package to do lexing and SLR parsing, and produce as
# output an abstract syntax tree (defined in the Absyn module).

# The Translate module type-checks the code, maintains the symbol
# table (symbol.py) and converts it into an intermediate form (ir.py)

# Canon performs several simplifying passes on the IR to make it easier
# to deal with, then codegen converts it into a linear sequence of
# simple C instructions

# Finally we invoke the C compiler to convert to a native code shared library

# import getopt
import sys
# import commands
import os.path
import stat
import random
import hashlib
import re
import copy

#import fractconfig
#import translate
# import fracttypes
#import absyn
# import cache
#import gradient
from LiuD import ParseFormFile

class FormulaTypes:
    FRACTAL = 0
    COLORFUNC = 1
    TRANSFORM = 2
    GRADIENT = 3
    NTYPES = 4

    GRAD_UGR=0
    GRAD_MAP=1
    GRAD_GGR=2
    GRAD_CS=3
    matches = [
        re.compile(r'(\.frm\Z)|(\.ufm\Z)', re.IGNORECASE),
        re.compile(r'(\.cfrm\Z)|(\.ucl\Z)', re.IGNORECASE),
        re.compile(r'\.uxf\Z', re.IGNORECASE),
        re.compile(r'(\.ugr\Z)|(\.map\Z)|(\.ggr\Z)|(\.cs\Z)|(\.pal\Z)', re.IGNORECASE)
        ]

    # indexed by FormulaTypes above
    extensions = [ "frm", "cfrm", "uxf", "ggr", "pal"]

    @staticmethod
    def extension_from_type(t):
        return FormulaTypes.extensions[t]

    @staticmethod
    def guess_formula_type_from_filename(filename):
        for i in xrange(FormulaTypes.NTYPES):
            if FormulaTypes.matches[i].search(filename):
                return i
        raise ValueError("Unknown file type for '%s'" % filename)

    @staticmethod
    def guess_gradient_subtype_from_filename(filename):
        filename = filename.lower()
        if filename.endswith(".ugr"):
            return FormulaTypes.GRAD_UGR
        if filename.endswith(".map") or filename.endswith(".pal"):
            return FormulaTypes.GRAD_MAP
        if filename.endswith(".ggr"):
            return FormulaTypes.GRAD_GGR
        if filename.endswith(".cs"):
            return FormulaTypes.GRAD_CS
        raise ValueError("Unknown gradient type for '%s'" % filename)

    @staticmethod
    def isFormula(filename):
        for matcher in FormulaTypes.matches:
            if matcher.search(filename):
                return True
        return False

class FormulaFile:
    def __init__(self, formulas, contents,mtime,filename):
        self.formulas = formulas
        self.contents = contents
        self.mtime = mtime
        self.filename = filename

    def out_of_date(self):
        return os.stat(self.filename)[stat.ST_MTIME] > self.mtime

    def get_formula(self,formula):
        return self.formulas.get(formula)

    def get_formula_names(self, skip_type=None):
        '''return all the coloring funcs except those marked as only suitable
        for the OTHER kind (inside vs outside)'''
        names = []
        for name in self.formulas.keys():
            sym = self.formulas[name].symmetry
            if sym == None  or sym == "BOTH" or sym != skip_type:
                names.append(name)

        return names

class Compiler:
    def __init__(self):
        self.path_lists = [ [], [], [], [] ]
        self.files = {}

        self.leave_dirty = False

    def add_path(self,path,type):
        self.path_lists[type].append(path)

    def add_func_path(self,path):
        self.path_lists[FormulaTypes.FRACTAL].append(path)
        self.path_lists[FormulaTypes.COLORFUNC].append(path)
        self.path_lists[FormulaTypes.TRANSFORM].append(path)

    def find_files(self,type):
        files = {}
        for dir in self.path_lists[type]:
            if not os.path.isdir(dir):
                continue
            for file in os.listdir(dir):
                if os.path.isfile(os.path.join(dir,file)):
                    files[file] = 1
        return files.keys()

    def add_inline_formula(self,formbody):
        # formbody contains a string containing the contents of a formula
        mod = ParseFormFile.ParseFormuFile_deep(formbody)
        name = mod.n.strip()
        return name, mod

    def find_file(self,filename,type):
        if os.path.exists(filename):
            dir = os.path.dirname(filename)
            if self.path_lists[type].count(dir) == 0:
                # add directory to search path
                self.path_lists[type].append(dir)
            return filename

        filename = os.path.basename(filename)
        for path in self.path_lists[type]:
            f = os.path.join(path,filename)
            if os.path.exists(f):
                return f

        return None

    def parse_file(self, s):
        # print 'input', type(s), len(s)
        return ParseFormFile.ParseFormuFile_nodeep(s)

    def load_formula_file(self, filename):
        try:
            type = FormulaTypes.guess_formula_type_from_filename(filename)
            filename = self.find_file(filename,type)
            s = open(filename,"r").read() # read in a whole file
            basefile = os.path.basename(filename)
            mtime = os.stat(filename)[stat.ST_MTIME]

            if type == FormulaTypes.GRADIENT:
                # don't try and parse gradient files apart from UGRs
                subtype = FormulaTypes.guess_gradient_subtype_from_filename(filename)
                if subtype == FormulaTypes.GRAD_UGR:
                    formulas = self.parse_file(s)
                else:
                    formulas = {}
            else:
                print 'formula file:', filename
                formulas = self.parse_file(s)

            ff = FormulaFile(formulas,s,mtime,filename)
            self.files[basefile] = ff

            return ff
        except Exception, err:
            #print "Error parsing '%s' : %s" % (filename, err)
            raise

    def out_of_date(self,filename):
        basefile = os.path.basename(filename)
        ff = self.files.get(basefile)
        if not ff:
            self.load_formula_file(filename)
            ff = self.files.get(basefile)
        return ff.out_of_date()

    def get_file(self,filename):
        basefile = os.path.basename(filename)
        ff = self.files.get(basefile)
        if not ff:
            self.load_formula_file(filename)
            ff = self.files.get(basefile)
        elif ff.out_of_date():
            self.load_formula_file(filename)
            ff = self.files.get(basefile)
        return ff

    def get_parsetree(self,filename,formname):
        ff = self.get_file(filename)
        if ff == None : return None
        return ff.get_formula(formname)

    def get_formula_3(self, mod):
        return TT(mod)


class TT:
    def __init__(self, mod):
        self.mod = mod
    def GetDefaultValues(self):
        import fractal
        return fractal.GetDefaultVals(self.mod)


