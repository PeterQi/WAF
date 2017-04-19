#!/usr/bin/env python
#coding:utf-8
import re
import math
import xml.etree.ElementTree as ET
def xml_read():
    tree = ET.parse("payload.xml")
    root = tree.getroot()
    count = 0
    al_num = 0
    max_len = 0
    times = 0
    eff = []
    pre_eff = []
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            keywords = level.findall("keywords")
            keywords_text = []
            for keyword in keywords:
                for e in eff:
                    if e in keyword.text:
                        flag = False
                        if e not in pre_eff:
                            pre_eff.append(e)
                keywords_text.append(keyword.text)
            eff += keywords_text
    print pre_eff
            
def teststr_l(s, eff):
    i = 0
    j = 0
    len1 = len(eff)
    len2 = len(s)
    flag = False
    while i < len1 and j < len2:
        if eff[i] == s[j]:
            i += 1
        j += 1
    if i >= len1:
        return True
    else:
        return False
if __name__ == "__main__":
    xml_read()
    