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
    re = requests.get("http://www.python-requests.org/en/master/user/quickstart/#binary-response-content")
    print re.headers
if __name__ == "__main__":
    test()
    