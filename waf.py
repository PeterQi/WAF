#coding=utf-8
import requests
from optparse import OptionParser
import os
import difflib
import urlparse
import urllib

MAIN_PATH = os.path.abspath('.')
STANDARD_RATIO = 0
RESPONSES = []
SIMILARITY = []
METHOD_POST = 2
METHOD_GET = 1
NOT_FOUND = 0
ACCEPTABLE_DIFF_RATIO = 0.05



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
    if not options.url or not options.param:
        parser.error("Missing argument for target url or target param. Use '-h' for help.")
    return options
    
def first_request(options):
    headers = {}
    if options.cookie:
        headers["Cookie"] = options.cookie
    if options.header:
        headers[options.header.split("=")[0]] = options.header.split("=", 1)[1]
    if options.data:
        req = requests.post(options.url,headers=headers,data=options.data)
    else:
        req = requests.get(options.url,headers=headers)
    return req

def get_standard_ratio(opt):
    global STANDARD_RATIO
    print opt.url+' is responsing'
    req1 = first_request(opt)
    RESPONSES.append(req1)
    print opt.url+' is responsing'
    req2 = first_request(opt)
    print 'top similarity:', 
    STANDARD_RATIO = difflib.SequenceMatcher(None, req1.content, req2.content).ratio()
    print STANDARD_RATIO
    return STANDARD_RATIO

def send_fixed_request(opt, query_list, str, offset, post = False):
    headers = {}
    query_list[offset] = (opt.param, str)
    if opt.cookie:
        headers["Cookie"] = opt.cookie
    if opt.header:
        headers[opt.header.split("=")[0]] = options.header.split("=", 1)[1]
    if post:
        req = requests.post(opt.url,headers = headers, data = query_list)
        return req
    geturl = urlparse.urlparse(opt.url)
    url = urlparse.urlunparse((geturl.scheme, geturl.netloc, geturl.path, geturl.params, "", geturl.fragment))
    req = requests.get(url,headers = headers, params = query_list)
    return req
        
def find_param_offset(param_name, url_qs):
    query_list = urlparse.parse_qsl(url_qs)
    aim_param_offset = -1
    for i in range(len(query_list)):
        if query_list[i][0] == param_name:
            aim_param_offset = i
        query_list[i] = (query_list[i][0], urllib.unquote(query_list[i][1]))
    return query_list, aim_param_offset
    
def find_param_method(opt):
    query_list = []
    offset = -1
    if opt.data:
        query_list, offset = find_param_offset(opt.param, opt.data)
    if offset != -1:
        return query_list, offset, METHOD_POST
    query_list, offset = find_param_offset(opt.param, urlparse.urlparse(opt.url).query)
    if offset != -1:
        return query_list, offset, METHOD_GET
    return query_list, offset, NOT_FOUND
    
def get_all_features(opt):
    param_NULL = ""
    param_NUM = 100
    param_STR = "hello"
    param_SPECIAL = "!\"$%&\\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r#\x0b\x0c"
    param_EVIL = "AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(\"XSS\")</script>',table_name FROM information_schema.tables WHERE 2>1--/**/; EXEC xp_cmdshell('cat ../../../etc/passwd')#"
    
    query_list, offset, method = find_param_method(opt)
    
    if method == METHOD_POST:
        req = send_fixed_request(opt, query_list, param_NULL, offset, True)
        print 'sent fixed request 1'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_NUM, offset, True)
        print 'sent fixed request 2'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_STR, offset, True)
        print 'sent fixed request 3'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_SPECIAL, offset, True)
        print 'sent fixed request 4'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_EVIL, offset, True)
        print 'sent fixed request 5'
        RESPONSES.append(req)
    elif method == METHOD_GET:
        req = send_fixed_request(opt, query_list, param_NULL, offset)
        print 'sent fixed request 1'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_NUM, offset)
        print 'sent fixed request 2'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_STR, offset)
        print 'sent fixed request 3'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_SPECIAL, offset)
        print 'sent fixed request 4'
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_EVIL, offset)
        print 'sent fixed request 5'
        RESPONSES.append(req)
    else:
        print "Invaild Param:"+opt.param
        return -1
    print 'start computing similarity...'
    compute_similarity()
    len_of_res = len(RESPONSES)
    i = 0
    while i < len_of_res:
        group_offset = i#记录本响应结果的归类号
        for j in range(i):
            if STANDARD_RATIO - SIMILARITY[i][j] < ACCEPTABLE_DIFF_RATIO:
                group_offset = j
                break
        if group_offset != i:
            for k in range(i+1, len(RESPONSES)):
                del(SIMILARITY[k][i])
            del(SIMILARITY[i])
            del(RESPONSES[i])
            i -= 1
            len_of_res -= 1
        i += 1
    return len_of_res
    
def compute_similarity():
    global SIMILARITY
    SIMILARITY = []
    for i in range(len(RESPONSES)):
        line_similarity = []
        for j in range(i):
            line_similarity.append(difflib.SequenceMatcher(None, RESPONSES[i].content, RESPONSES[j].content).ratio())
        print line_similarity
        SIMILARITY.append(line_similarity)
    
def response2file():
    for i in range(len(RESPONSES)):
        f = open('test'+str(i)+'.html','w')
        f.write(RESPONSES[i].content)
        f.close()

def test(opt):
    get_standard_ratio(opt)
    group = get_all_features(opt)
    response2file()
    print SIMILARITY
    
def main():
    opt = parse_cmd_args()
    if opt.test:
        test(opt)
        return
    first_request(opt)
    from sys import path
    path.append(MAIN_PATH+'/sqlmap')
    from sqlmap import sqlmain
    print sqlmain(['sqlmap.py', '-u', opt.url, '--identify-waf'])
if __name__=="__main__":
    main()