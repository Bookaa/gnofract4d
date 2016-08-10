#!/usr/bin/env python

import shutil
from distutils.core import setup, Extension
import distutils.sysconfig
import os
import stat
import commands
import sys

gnofract4d_version = '3.14.1'

if float(sys.version[:3]) < 2.4:
    print "Sorry, you need Python 2.4 or higher to run Gnofract 4D."
    print "You have version %s. Please upgrade." % sys.version
    sys.exit(1)

# by default python uses all the args which were used to compile it. But Python is C and some
# extension files are C++, resulting in annoying '-Wstrict-prototypes is not supported' messages.
# tweak the cflags to override
os.environ["CFLAGS"]= distutils.sysconfig.get_config_var("CFLAGS").replace("-Wstrict-prototypes","")
os.environ["OPT"]= distutils.sysconfig.get_config_var("OPT").replace("-Wstrict-prototypes","")

from buildtools import my_install_lib

# Extensions need to link against appropriate libs
# We use pkg-config to find the appropriate set of includes and libs

def call_package_config(package,option,optional=False):
    '''invoke pkg-config, if it exists, to find the appropriate
    arguments for a library'''
    cmd = "pkg-config %s %s" % (package, option)
    (status,output) = commands.getstatusoutput(cmd)
    if status != 0:
        if optional:
            print >>sys.stderr, "Can't find '%s'" % package
            print >>sys.stderr, "Some functionality will be disabled"
            return []
        else:
            print >>sys.stderr, "Can't set up. Error running '%s'." % cmd
            print >>sys.stderr, output
            print >>sys.stderr, "Possibly you don't have one of these installed: '%s'." % package
            sys.exit(1)

    return output.split()

extra_macros = []

png_flags = call_package_config("libpng", "--cflags", True)
if png_flags != []:
    extra_macros.append(('PNG_ENABLED', 1))
else:
    raise Exception("NO PNG HEADERS FOUND, you need to install libpng-dev")
    
png_libs = call_package_config("libpng", "--libs", True)

jpg_lib = "jpeg"
if os.path.isfile("/usr/local/include/jpeglib.h"):
    extra_macros.append(('JPG_ENABLED', 1))
    jpg_libs = [ jpg_lib ]
else:
    raise Exception("NO JPEG HEADERS FOUND, you need to install libjpeg-dev")
    jpg_libs = []

#not ready yet. 
have_gmp = False # os.path.isfile("/usr/include/gmp.h")

# use currently specified compilers, not ones from when Python was compiled
# this is necessary for cross-compilation
compiler = os.environ.get("CC","gcc")
cxxcompiler = os.environ.get("CXX","g++")

fract4d_sources = [
    'fract4d/c/fract4dmodule.cpp',
    'fract4d/c/cmap.cpp',
    'fract4d/c/pointFunc.cpp',
    'fract4d/c/fractFunc.cpp',
    'fract4d/c/STFractWorker.cpp',
    'fract4d/c/image.cpp',
    'fract4d/c/imageIO.cpp',
    'fract4d/c/fract_stdlib.cpp'
    ]

defines = [ ('_REENTRANT',1),
            ('THREADS',1),
            #('STATIC_CALC',1),
            #('NO_CALC', 1),  # set this to not calculate the fractal
            #('DEBUG_CREATION',1), # debug spew for allocation of objects
            #('DEBUG_ALLOCATION',1), # debug spew for array handling
            ]

if 'win' == sys.platform[:3]:
    warnings = '/W3'
    libs = [ 'pthreadVC2', 'libdl' ]
    osdep = [ '/DWIN32', '/DWINDOWS', '/D_USE_MATH_DEFINES', '/D_CRT_SECURE_NO_WARNINGS', '/EHsc', '/Ox' ]
    osdep += [ '/I"F:/Gamma/GTK+/Win32/include/glib-2.0/"', '/I"F:/Gamma/GTK+/Win32/lib/glib-2.0/include/"' ]
    extra_source = [ 'fract4d/c/win32func.cpp', 'fract4d/c/fract4d_stdlib_exports.cpp' ]
    extra_link = [ '/LIBPATH:"F:/Gamma/GTK+/Win32/lib"' ]
else:
    warnings = '-Wall'
    libs = [ 'stdc++' ]
    osdep = []
    extra_source = []
    extra_link = []

fract4d_sources += extra_source

module_fract4dc = Extension(
    'fract4d.fract4dc',
    sources = fract4d_sources,
    include_dirs = [
    'fract4d/c'
    ],
    libraries = libs + jpg_libs,
    extra_compile_args = [
    warnings,
    ] + osdep + png_flags,
    extra_link_args = extra_link + png_libs,
    define_macros = defines + extra_macros,
    #undef_macros = [ 'NDEBUG'],
    )

module_cmap = Extension(
    'fract4d.fract4d_stdlib',
    sources = [
    'fract4d/c/cmap.cpp',
    'fract4d/c/image.cpp',
    'fract4d/c/fract_stdlib.cpp'
    ] + extra_source,
    include_dirs = [
    'fract4d/c'
    ],
    libraries = libs,
    extra_link_args = extra_link,
    define_macros = [ ('_REENTRANT', 1)]
    )

modules = [module_fract4dc, module_cmap]
    
def get_files(dir,ext):
    return [ os.path.join(dir,x) for x in os.listdir(dir) if x.endswith(ext)] 

setup (name = 'gnofract4d',
       version = gnofract4d_version,
       description = 'A program to draw fractals',
       long_description = \
'''Gnofract 4D is a fractal browser. It can generate many different fractals, 
including some which are hybrids between the Mandelbrot and Julia sets,
and includes a Fractint-compatible parser for your own fractal formulas.''',
       author = 'Edwin Young',
       author_email = 'edwin@bathysphere.org',
       maintainer = 'Edwin Young',
       maintainer_email = 'catenary@users.sourceforge.net',
       keywords = "edwin@bathysphere.org",
       url = 'http://github.com/edyoung/gnofract4d/',
       packages = ['fract4d', ],
       package_data = {  },
       ext_modules = modules,
       scripts = [],
       data_files = [
           # color maps
           ('share/gnofract4d/maps',
            get_files("maps",".map") +
            get_files("maps",".cs") +
            get_files("maps", ".ugr")),

           # formulas
           ('share/gnofract4d/formulas',
            get_files("formulas","frm") +
            get_files("formulas", "ucl") +
            get_files("formulas", "uxf")),

           # documentation

           #internal pixmaps
           ('share/pixmaps/gnofract4d',
            ['pixmaps/improve_now.png',
             'pixmaps/explorer_mode.png']),

           # icon
           ('share/pixmaps',
            ['pixmaps/gnofract4d-logo.png']),
           
           # .desktop file
           ('share/applications', ['gnofract4d.desktop']),

           # MIME type registration
           ('share/mime/packages', ['gnofract4d-mime.xml']),
           
           # doc files
           ('share/doc/gnofract4d/',
            ['COPYING', 'README']),
           ],
       cmdclass={
           "install_lib" : my_install_lib.my_install_lib           
           }
       )

# I need to find the file I just built and copy it up out of the build
# location so it's possible to run without installing. Can't find a good
# way to extract the actual target directory out of distutils, hence
# this egregious hack

so_extension = distutils.sysconfig.get_config_var("SO")

lib_targets = {
    "fract4dc" + so_extension : "fract4d",
    "fract4d_stdlib" + so_extension : "fract4d",
    "fract4dcgmp" + so_extension : "fract4d",
    "gmpy" + so_extension: "fract4d"
    }
if 'win' == sys.platform[:3]:
    lib_targets["fract4d_stdlib.lib"] = "fract4d"

def copy_libs(dummy,dirpath,namelist):
     for name in namelist:
         target = lib_targets.get(name)
         if target != None:
             name = os.path.join(dirpath, name)
             shutil.copy(name, target)
            
os.path.walk("build",copy_libs,None)
if 'win' == sys.platform[:3]:
    shutil.copy("fract4d/fract4d_stdlib.pyd", "fract4d_stdlib.pyd")

