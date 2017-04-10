#!/usr/bin/env python
#coding:utf-8
import xml.etree.ElementTree as ET
def test():
    tree = ET.parse("test.xml")
    root = tree.getroot()
    for type in root:
        for level in type:
            print level.tag, level.attrib['bound']
            sen = level.find("sentences")
            print sen.text
            keywords = level.findall("keywords")
            for keyword in keywords:
                print keyword.text
                
if __name__ == "__main__":
    test()
    