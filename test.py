#!/usr/bin/env python
#coding:utf-8
#python waf.py -u "http://www.esri.com/search?q=and" -p q -t 40 --test
#python waf.py -u "http://constitutionus.com/?id=and" -p id -t 40 -r "<script.*</script>" --test
import xml.etree.ElementTree as ET
import random
import threadpool
import os
import math
import copy
import re

def teststr_reg(s, eff):
    data = re.search(eff, s)
    if data == None:
        return False
    else:
        if len(data.group(0)) == 0:
            return False
        else:
            return True

def case_switch(st):
    C_st = ""
    flag = False
    for c in st:
        ascii = ord(c)
        if ascii >= 65 and ascii <= 90:
            flag = True
            if random.randint(0,1):
                C_st += c.lower()
            else:
                C_st += c
        elif ascii >= 97 and ascii <= 122:
            flag = True
            if random.randint(0,1):
                C_st += c.upper()
            else:
                C_st += c
        else:
            C_st += c
    if not flag:
        return st
    if C_st == st:
        C_st = case_switch(st)
    return C_st
        
def rand_chr(chrs, banned = ""):
    if len(chrs) == 1:
        return chr(chrs[0])
    elif len(chrs) == 0:
        return ''
    c = chr(chrs[random.randint(0, len(chrs)-1)])
    if c == banned.lower() or c == banned.upper():
        c = rand_chr(chrs, banned)
    return c
    
        
def replace_chr(st, offset, eff=''):
    w_chrs = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
    WS_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    sN_chrs = [9, 11, 12, 13, 32]
    dot_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    d_chrs = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    D_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    W_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    s_chrs = [9, 10, 11, 12, 13, 32]
    S_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    if offset < 0 or offset >= len(st):
        return ''
    test_st = copy.copy(st)
    test_st = test_st[:offset] + chr(10) + test_st[offset+1:]
    #print test_st
    if st[offset] == test_st[offset] or teststr_reg(test_st, eff):
        sec_test = rand_chr(w_chrs, st[offset])
        test_st = test_st[:offset] + sec_test + test_st[offset+1:]
        if teststr_reg(test_st, eff):
            return '\D'
        else:
            trd_test = rand_chr(WS_chrs, st[offset])
            test_st = test_st[:offset] + trd_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                return '\W'
            else:
                return '\s'
    else:
        sec_test = rand_chr(w_chrs, st[offset])
        test_st = test_st[:offset] + sec_test + test_st[offset+1:]
        if teststr_reg(test_st, eff):
            trd_test = rand_chr(WS_chrs, st[offset])
            test_st = test_st[:offset] + trd_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                fth_test = rand_chr(sN_chrs, st[offset])
                test_st = test_st[:offset] + fth_test + test_st[offset+1:]
                if teststr_reg(test_st, eff):
                    return '.'
                else:
                    return '\S'
            else:
                return '\w'
        else:
            d_test = rand_chr(d_chrs, st[offset])
            test_st = test_st[:offset] + d_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                return '\d'
            else:
                return st[offset]
                   
def insert_chr(st, offset, eff=''):
    w_chrs = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
    WS_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    sN_chrs = [9, 11, 12, 13, 32]
    dot_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    d_chrs = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    D_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    W_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    s_chrs = [9, 10, 11, 12, 13, 32]
    S_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    if offset <= 0 or offset >= len(st):
        return ''
    pattern = ''
    test_st = copy.copy(st)
    test_st = st[:offset] + chr(10) + st[offset:]
    if teststr_reg(test_st, eff):
        sec_test = rand_chr(w_chrs)
        test_st = st[:offset] + sec_test + st[offset:]
        if teststr_reg(test_st, eff):
            pattern = '\D'
            test_st = st[:offset]
            for i in range(10):
                multi_test = rand_chr(D_chrs)
                test_st += multi_test
            test_st += st[offset:]
            if teststr_reg(test_st, eff):
                return pattern+'*'
            else:
                return pattern
        else:
            trd_test = rand_chr(WS_chrs)
            test_st = st[:offset] + trd_test + st[offset:]
            if teststr_reg(test_st, eff):
                pattern = '\W'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(W_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern
            else:
                pattern = '\s'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(s_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern
    else:
        sec_test = rand_chr(w_chrs)
        test_st = st[:offset] + sec_test + st[offset:]
        if teststr_reg(test_st, eff):
            trd_test = rand_chr(WS_chrs)
            test_st = st[:offset] + trd_test + st[offset:]
            if teststr_reg(test_st, eff):
                fth_test = rand_chr(sN_chrs)
                test_st = st[:offset] + fth_test + st[offset:]
                if teststr_reg(test_st, eff):
                    pattern = '.'
                    test_st = st[:offset]
                    for i in range(10):
                        multi_test = rand_chr(dot_chrs)
                        test_st += multi_test
                    test_st += st[offset:]
                    if teststr_reg(test_st, eff):
                        return pattern+'*'
                    else:
                        return pattern
                else:
                    pattern = '\S'
                    test_st = st[:offset]
                    for i in range(10):
                        multi_test = rand_chr(S_chrs)
                        test_st += multi_test
                    test_st += st[offset:]
                    if teststr_reg(test_st, eff):
                        return pattern+'*'
                    else:
                        return pattern
                    
            else:
                pattern = '\w'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(w_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern
        else:
            d_test = rand_chr(d_chrs)
            test_st = st[:offset] + d_test + st[offset:]
            if teststr_reg(test_st, eff):
                pattern = '\d'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(d_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern
            else:
                return ''
    
def case_chr(st, eff):
    test_st = case_switch(st)
    if teststr_reg(test_st, eff):
        return True
    else:
        return False
    
def get_reg(st, eff=''):
    result = ''
    for i in range(len(st)):
        result += insert_chr(st, i, eff)
        result += replace_chr(st, i, eff)
    if case_chr(st, eff):
        result = '(?i)'+result
    return result

def regular_special(ch):
    if ch in '$()*+.[]?\\{}|':
        return '\\' + ch
    else:
        return ch
    
if __name__ == "__main__":
    print get_reg('<scpri pt>', '.*<\W*s\w*c\Dr\d*i\sp\S*t.*>.*')