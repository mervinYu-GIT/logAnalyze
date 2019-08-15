#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
from itertools import izip


def getFileList( p ):
    """ get file name that in dictory. """
    p = str( p )
    if p=="":
        return [ ]
    p = p.replace( "/","\\")
    if p[ -1] != "\\":
        p = p+"\\"
    a = os.listdir( p )
    b = [ x   for x in a if os.path.isfile( p + x ) ]
    return b


# sort string containning numbers
re_digits = re.compile(r'(\d+)')  
def embedded_numbers(s):  
     pieces = re_digits.split(s)               # split num and asc  
     pieces[1::2] = map(int, pieces[1::2])     # exchange the num  
     return pieces  


def sort_strings_with_embedded_numbers(alist):  
     return sorted(alist, key=embedded_numbers , reverse = True)


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)