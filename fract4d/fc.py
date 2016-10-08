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
import translate
# import fracttypes
import absyn
# import cache
import gradient

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
    def guess_type_from_filename(filename):
        if FormulaTypes.matches[FormulaTypes.FRACTAL].search(filename):
            return translate.T
        elif FormulaTypes.matches[FormulaTypes.COLORFUNC].search(filename):
            return translate.ColorFunc
        elif FormulaTypes.matches[FormulaTypes.TRANSFORM].search(filename):
            return translate.Transform
        elif FormulaTypes.matches[FormulaTypes.GRADIENT].search(filename):
            return translate.GradientFunc

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

    def find_files_of_type(self,type):
        matcher = FormulaTypes.matches[type]
        return [file for file in self.find_files(type)
                if matcher.search(file)]

    def find_formula_files(self):
        return self.find_files_of_type(FormulaTypes.FRACTAL)

    def find_colorfunc_files(self):
        return self.find_files_of_type(FormulaTypes.COLORFUNC)

    def find_transform_files(self):
        return self.find_files_of_type(FormulaTypes.TRANSFORM)

    def add_inline_formula(self,formbody, formtype):
        # formbody contains a string containing the contents of a formula
        form = self.parse_file_detail(formbody)
        return form.leaf, form

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

    def parse_file_detail(self, s):
        dict_ = ParseFormulaFileRemote_detail(s)
        chil = dict_['children']
        assert len(chil) == 1
        v = chil[0]
        return absyn.Node1(v)

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

    def get_formula_text(self,filename,formname):
        ff = self.get_file(filename)
        form = ff.get_formula(formname)
        start_line = form.pos-1
        last_line = form.last_line
        lines = ff.contents.splitlines()
        return "\n".join(lines[start_line:last_line])

    def get_parsetree(self,filename,formname):
        ff = self.get_file(filename)
        if ff == None : return None
        return ff.get_formula(formname)

    def guess_type_from_filename(self,filename):
        return FormulaTypes.guess_type_from_filename(filename)

    def get_formula_3(self, form, formtype, prefix):
        if formtype == 0:
            type = translate.T
        elif formtype == 1:
            type = translate.ColorFunc
        elif formtype == 2:
            type = translate.Transform
        elif formtype == 3:
            type = translate.GradientFunc

        f = form

        if f != None:
            return type(f, prefix)

        return f

    def get_formula(self, filename, formname,prefix=""):
        type = self.guess_type_from_filename(filename)

        f = self.get_parsetree(filename,formname)

        if f != None:
            f = type(f,prefix)
        return f

    def get_formula_with_text(self, type, formulatext, prefix=""):

        f = self.get_parsetree_with_text(formulatext)

        if f != None:
            f2 = type(f,prefix)
            return f2, f.leaf
        return None, ''

    def get_gradient(self, filename, formname):
        g = gradient.Gradient()
        if formname == None:
            g.load(open(self.find_file(filename, 3))) # FIXME
        else:
            compiled_gradient = self.get_formula(filename,formname)
            g.load_ugr(compiled_gradient)

        return g

    def get_random_gradient(self):
        return self.get_random_formula(3) # FIXME

    def get_random_formula(self,type):
        files = self.find_files_of_type(type)
        file = random.choice(files)

        if gradient.FileType.guess(file) == gradient.FileType.UGR:
            ff = self.get_file(file)
            formulas = ff.formulas.keys()
            formula = random.choice(formulas)
        else:
            formula = None
        return (file,formula)


from LiuD import ParseFormFile

def ParseFormulaFileRemote_detail(s):
    dict3_ = ParseFormFile.ParseFormuFile_deep(s)
    return dict3_
