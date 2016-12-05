#!/usr/bin/env python

import os
path1=os.path.abspath('.')


if __name__ == "__main__":
    from sys import path
    path.append(path1+'/sqlmap')
    from sqlmap import *
    print sqlmain(['sqlmap.py', '-u', 'http://bbs.125.la/plugin.php', '--identify-waf'])
    