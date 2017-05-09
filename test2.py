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
def print_result(num):
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print 'stop'
    except:
        pass
    
def exit_thread(request, result):
    return 
    
def test():
    pool = threadpool.ThreadPool(5)
    reqs = threadpool.makeRequests(print_result,[((),{'num':j})for j in range(5)], exit_thread)
    [pool.putRequest(req) for req in reqs]
    try:
        pool.wait()
    except Exception as e:
        print 'error'
if __name__ == "__main__":
    test()
    