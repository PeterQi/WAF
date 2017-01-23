#!/usr/bin/env python
import difflib



if __name__ == "__main__":
    f1 = open('test1.html')
    f1content = f1.read()
    f1.close()
    f2 = open('test1.html')
    f2content = f2.read()
    f2.close()
    print difflib.SequenceMatcher(None, f1content, f2content).ratio()