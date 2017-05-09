#!/usr/bin/env python
#coding:utf-8
#python waf.py -u "http://www.esri.com/search?q=and" -p q -t 40 --test
#python waf.py -u "http://constitutionus.com/?id=and" -p id -t 40 -r "<script.*</script>" --test
import xml.etree.ElementTree as ET
import random
import threadpool
import os
import gc

def threads_payloads2(i):
    print i,
    os.exit()
    
def thread_payload1(i):
    print 'a',
    return
if __name__ == "__main__":
    opt = 400
    pool = threadpool.ThreadPool(opt)
    for i in range(25):
        try:
            reqs = threadpool.makeRequests(threads_payloads2,[((),{'i':j})for j in range(opt)])
            [pool.putRequest(req) for req in reqs]
            pool.wait()
        except Exception, e:
            print Exception,e
    for i in range(25):
        try:
            reqs = threadpool.makeRequests(thread_payload1,[((),{'i':j})for j in range(opt)])
            [pool.putRequest(req) for req in reqs]
            pool.wait()
        except Exception, e:
            print Exception,e