#!/usr/bin/env python
import requests
from optparse import OptionParser

def parse_cmd_args():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-u", "--url", dest="url", help="set target URL")
    parser.add_option("-p", "--param", dest="param",
                      help="set parameter name to test for (e.g. \"page\")")
    parser.add_option("-d", "--data", dest="data",
                      help="set data for HTTP POST request (e.g. \"page=default\")")
    parser.add_option("--cookie", dest="cookie",
                      help="set HTTP Cookie header value (e.g. \"sid=foobar\")")
    parser.add_option("--header", dest="header",
                      help="set a custom HTTP header (e.g. \"Max-Forwards=10\")")
    parser.add_option("--test", dest="test", action = "store_true",
                      help="make a test")
    (options, args) = parser.parse_args()
    #if not options.url or not options.param:
     #   parser.error("Missing argument for target url or target param. Use '-h' for help.")
    return options

if __name__ == "__main__":
    f = open('./abc/b', 'w')
    f.write(1)
    f.close()