#!/usr/bin/env python
#coding:utf-8
#python waf.py -u "http://www.esri.com/search?q=and" -p q -t 40 --test
#python waf.py -u "http://constitutionus.com/?id=and" -p id -t 40 -r "<script.*</script>" --test
import xml.etree.ElementTree as ET
import random
import os
def combination(keywords, n):
    com = []
    m = len(keywords)
    if n > m:
        return []
    if n == m:
        s = ""
        for k in keywords:
            s += k
        return [s]
    if n < 0:
        return []
    A = combination(keywords[:-1], n-1)
    for i in range(len(A)):
        A[i] += keywords[-1]
    B = combination(keywords[:-1], n)
    com = A + B
    return com

def xml_read():
    tree = ET.parse("special.xml")
    root = tree.getroot()
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            count = 1
            print sentence
            keywords = level.findall("keywords")
            keywords_text = []
            for keyword in keywords:
                keywords_text.append(keyword.text)
            for i in range(1,bound + 1):
                c = combination(keywords_text, i)
                for k in c:
                    print count, k
                    count += 1
def teststr(s, eff):
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
class node:
    value = ""
    parent = None
    left_son = None
    right_son = None
    sibling = -1#0是左儿子，1是右儿子
    root = 0#层级，0为根
    need_extra = True#需要加上其他的
    eff_flag = False#测试成功
    def node_value_ex(self):
        if self.root == 0:
            return self.value
        else:
            tmp_val = self.value
            tmp_node = self
            while tmp_node.parent.root != 0:
                if tmp_node.parent.sibling == 0:
                    tmp_val += tmp_node.parent.parent.right_son.value
                else:
                    tmp_val = tmp_node.parent.parent.left_son.value + tmp_val
                tmp_node = tmp_node.parent
            return tmp_val
    def tree_values(self):
        if self.root != 0:
            print self.value
            return
        else:
            qu = [self]
            flag = False
            while len(qu) != 0:
                tmp_node = qu[0]
                del qu[0]
                print tmp_node.node_value_ex()
                if tmp_node.left_son != None:
                    qu.append(tmp_node.left_son)
                    qu.append(tmp_node.right_son)
    def find_effect(self):
        qu = []
        eff = ''
        if teststr(self.value):
            self.eff_flag = True
            if self.left_son != None:
                self.left_son.need_extra = False
                self.right_son.need_extra = False
                qu.append(self.left_son)
                qu.append(self.right_son)
            else:
                return self.value
        else:
            return eff
        while len(qu) != 0:
            tmp_node = qu[0]
            del qu[0]
            if not tmp_node.need_extra:
                if teststr(tmp_node.value):
                    qu = []
                    tmp_node.eff_flag = True
                    if tmp_node.left_son != None:
                        tmp_node.left_son.need_extra = False
                        tmp_node.right_son.need_extra = False
                        qu.append(tmp_node.left_son)
                        qu.append(tmp_node.right_son)
                    else:
                        eff += tmp_node.value
                else:
                    tmp_node.eff_flag = False
                    if tmp_node.parent.eff_flag and not tmp_node.parent.need_extra and not tmp_node.parent.left_son.eff_flag:
                        eff += tmp_node.parent.value
                    elif tmp_node.left_son != None:
                        qu.append(tmp_node.left_son)
                        qu.append(tmp_node.right_son)
                    else:
                        pass
            else:
                if teststr(tmp_node.node_value_ex()):
                    tmp_node.eff_flag = True
                    if tmp_node.left_son != None:
                        qu.append(tmp_node.left_son)
                        qu.append(tmp_node.right_son)
                    else:
                        eff += tmp_node.value
                else:
                    tmp_node.eff_flag = False
                    if tmp_node.left_son != None:
                        qu.append(tmp_node.left_son)
                        qu.append(tmp_node.right_son)
        return eff
    def construct_tree(self):
        length = len(self.value)
        if length <= 1:
            return
        mid = length / 2
        self.left_son = node()
        self.right_son = node()
        self.left_son.value = self.value[:mid]
        self.left_son.parent = self
        self.left_son.sibling = 0
        self.left_son.root = self.root + 1
        self.left_son.eff_flag = False
        self.right_son.value = self.value[mid:]
        self.right_son.parent = self
        self.right_son.sibling = 1
        self.right_son.root = self.root + 1
        self.right_son.eff_flag = False
        self.left_son.construct_tree()
        self.right_son.construct_tree()

def check_eff(s, test_eff):
    bound = len(s)
    eff = ""
    while bound > 0:
        start = 0
        end = bound
        left = start
        right = end
        if teststr(eff, test_eff):
            break
        while left < right - 1:
            mid = (left + right)/2
            if teststr(s[start:mid]+eff, test_eff):
                right = mid
            else:
                left = mid
        if not teststr(s[start:left]+eff, test_eff):
            left = right
        eff = s[left - 1] + eff
        bound = left - 1
    return eff
        
if __name__ == "__main__":
    #a = node()
    #a.need_extra = False
    #a.eff_flag = True
    #a.value = "abcdefg"
    #a.construct_tree()
    #print a.find_effect()
    a = raw_input()
    while a != '0':
        print check_eff("abcdefg", a)
        a = raw_input()
    