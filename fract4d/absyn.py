# Abstract Syntax Tree produced by parser

#from __future__ import generators
import types
import string
#import fracttypes
import re

class Node1:
    def __init__(self, dict_):
        if dict_ is None:
            self.dict_ = []
            return

        self.dict_ = dict_
        self.type = dict_['type']
        self.leaf = dict_['leaf']
        self.pos = dict_['pos']
        self.datatype = dict_['datatype']
        if 'symmetry' in dict_:
            self.symmetry = dict_['symmetry']
        if 'last_line' in dict_:
            self.last_line = dict_['last_line']
        if 'text' in dict_:
            self.text = dict_['text']
        if 'deepmod' in dict_:
            self.deepmod = dict_['deepmod']

        self.children = [Node1(v) for v in dict_['children']]

    def childByName(self,name):
        'find a child with leaf == name'
        for child in self.children:
            if child.leaf == name:
                return child
        return None

def NewNode(type,pos,children=None,leaf=None,datatype=None):
    if True:
        the = Node1(None)
        the.type = type
        the.children = children
        the.leaf = leaf
        the.datatype = datatype
        the.pos = pos
        return the
    return Node(type, pos, children, leaf, datatype)

