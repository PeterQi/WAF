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

cache = []
def test():
    f = open('./result/www.esri.com', 'r')
    a = f.read()
    b = a.split('\n')
    ALL = []
    l = len(b)
    for i in range(2, l - 2):
        if b[i] not in ALL:
            ALL.append(b[i])
    b = ALL
    print b
if __name__ == "__main__":
    test()