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

def test_ch(st):
    pool = threadpool.ThreadPool(10)
    reqs = threadpool.makeRequests(ok,[((),{'offset': i})for i in range(len(st))])
    [pool.putRequest(req) for req in reqs]
    pool.wait()
    
def ok(offset):
    print 'ook'
    
if __name__ == "__main__":
    test_ch('')