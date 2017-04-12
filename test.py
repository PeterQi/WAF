#!/usr/bin/env python
#coding:utf-8
import xml.etree.ElementTree as ET
import random
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
def teststr(s):
    a = random.randint(0,100)
    if a < 10:
        return True
    else:
        return False
class node:
    value = ""
    parent = None
    left_son = None
    right_son = None
    sibling = -1
    root = 0
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
        self.right_son.value = self.value[mid:]
        self.right_son.parent = self
        self.right_son.sibling = 1
        self.right_son.root = self.root + 1
        self.left_son.construct_tree()
        self.right_son.construct_tree()
if __name__ == "__main__":
    a = node()
    a.value = "abcdefg"
    a.construct_tree()
    a.tree_values()
    