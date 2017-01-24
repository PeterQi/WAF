#!/usr/bin/env python
#coding:utf-8
import difflib
import requests
STANDARD_RATIO = 1.0
SIMILARITY = []
ACCEPTABLE_DIFF_RATIO = 0.05
def compute_similarity():
    global SIMILARITY
    SIMILARITY = []
    for i in range(6):
        line_similarity = []
        f1 = open('test'+str(i)+'.html')
        content1 = f1.read()
        for j in range(i):
            f2 = open('test'+str(j)+'.html')
            content2 = f2.read()
            ra = difflib.SequenceMatcher(None, content1, content2).ratio()
            line_similarity.append(ra)
            f2.close()
        f1.close()
        print line_similarity
        SIMILARITY.append(line_similarity)
def test():
    re2 = None

    try:
        re2 = requests.get("http://www.japan.go.jp/initiatives/talks/", timeout = 0.622)
        print re2.elapsed.microseconds/1000000.0 + re2.elapsed.seconds
        print re2.elapsed.microseconds
    except Exception, e:
        re2 = None
    if re2 == None:
        print "re2 timeout"
if __name__ == "__main__":
    test()
    