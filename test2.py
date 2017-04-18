#!/usr/bin/env python
#coding:utf-8
import re
import xml.etree.ElementTree as ET
def xml_read():
    tree = ET.parse("payload.xml")
    root = tree.getroot()
    count = 0
    al_num = 0
    max_len = 0
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            keywords = level.findall("keywords")
            keywords_text = []
            for keyword in keywords:
                keywords_text.append(keyword.text)
            for k in keywords_text:
                count += 1
                l = len(k)
                al_num += l
                if l > max_len:
                    max_len = l
    print count
    print al_num
    print float(al_num)/float(count)
    print max_len
if __name__ == "__main__":
    xml_read()
    