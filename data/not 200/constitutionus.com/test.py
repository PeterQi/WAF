#!/usr/bin/env python
#coding:utf-8
import re
import math
import xml.etree.ElementTree as ET
import thread
import threadpool
import threading
import time
import sys
import difflib

def test():
    f = open('1.html', 'r')
    req1 = f.read()
    f.close()
    f = open('Not Acceptable!.html')
    req2 = f.read()
    f.close()
    regular = raw_input()
    p = re.compile(regular)
    t1 = p.search(req1)
    if t1 != None:
        g1 = t1.groups()
        if len(g1)>0:
            s1 = g1[0]
        else:
            s1 = t1.group()
    else:
        s1 = ''
    t2 = p.search(req2)
    if t2 != None:
        g2 = t2.groups()
        if len(g2)>0:
            s2 = g2[0]
        else:
            s2 = t2.group()
    else:
        s2 = ''
    print s1
    print s2
    STANDARD_RATIO = difflib.SequenceMatcher(None, s1, s2).ratio()
    print STANDARD_RATIO
    if regular == '0':
        return 0
    else:
        return 1
if __name__ == "__main__":
    while test():
        pass