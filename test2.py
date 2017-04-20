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
def test(s):
    try:
        cjlock.acquire()    
        time.sleep(2)
        print 'ok'
    except Exception, e:
        print Exception, e
        return -1
    return 1
def print_result(request, result):
    if result == -1:
        sys.exit()
if __name__ == "__main__":
    NUM = 5
    cache = []
    cjlock = threading.Lock()
    pool = threadpool.ThreadPool(NUM)
    reqs = threadpool.makeRequests(test,[((),{'s':j})for j in range(NUM)],print_result)
    [pool.putRequest(req) for req in reqs]
    while True:
        try:
            pool.wait()
        except KeyboardInterrupt:
            print 'sss'
            sys.exit()