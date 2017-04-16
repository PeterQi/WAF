#coding=utf-8
import requests
from optparse import OptionParser
import xml.etree.ElementTree as ET
import os
import difflib
import urlparse
import urllib
import sys

MAIN_PATH = os.path.abspath('.')
STANDARD_RATIO = 0
RESPONSES = []
TEST_RESPONSES = []
SIMILARITY = []
TEST_SIMILARITY = []
METHOD_POST = 2
METHOD_GET = 1
NOT_FOUND = 0
ACCEPTABLE_DIFF_RATIO = 0.05
BASE_RESPONSE_TIME = 60.0



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
    try:
        if options.data:
            req = requests.post(options.url,headers=headers,data=options.data, allow_redirects = False)
        else:
            req = requests.get(options.url,headers=headers, allow_redirects = False)
        return req
    except Exception, e:
        print Exception, ':', e
        sys.exit()
    
def get_standard_ratio(opt):
    global STANDARD_RATIO
    global BASE_RESPONSE_TIME
    print 'Original request is responsing'
    req1 = first_request(opt)
    RESPONSES.append(req1)
    req2 = first_request(opt)
    BASE_RESPONSE_TIME = (req1.elapsed.microseconds/1000000.0 + req1.elapsed.seconds + req2.elapsed.microseconds/1000000.0 + req2.elapsed.seconds)/2.0
    print 'Base response time:' + str(BASE_RESPONSE_TIME) + 's'
    print 'Top similarity:', 
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
    try:
        if post:
            req = requests.post(opt.url,headers = headers, data = query_list, allow_redirects = False, timeout = BASE_RESPONSE_TIME*30)
            return req
        geturl = urlparse.urlparse(opt.url)
        url = urlparse.urlunparse((geturl.scheme, geturl.netloc, geturl.path, geturl.params, "", geturl.fragment))
        req = requests.get(url,headers = headers, params = query_list, allow_redirects = False, timeout = BASE_RESPONSE_TIME*3)
    except Exception, e:
        req = None
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
    
    print 'sending mixed requests'
    if method == METHOD_POST:
        req = send_fixed_request(opt, query_list, param_NULL, offset, True)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_NUM, offset, True)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_STR, offset, True)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_SPECIAL, offset, True)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_EVIL, offset, True)
        RESPONSES.append(req)
    elif method == METHOD_GET:
        req = send_fixed_request(opt, query_list, param_NULL, offset)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_NUM, offset)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_STR, offset)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_SPECIAL, offset)
        RESPONSES.append(req)
        req = send_fixed_request(opt, query_list, param_EVIL, offset)
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
        if RESPONSES[i] != None:
            for j in range(i):
                if RESPONSES[j] != None:#双方均有响应的时候才继续计算相似度，否则直接判异同
                    if RESPONSES[i].status_code != 200:
                        if RESPONSES[j].status_code == RESPONSES[i].status_code:
                            line_similarity.append(1.0)
                        else:
                            line_similarity.append(0.0)
                    else:
                        if RESPONSES[j].status_code == 200:#响应码均为200才计算内容相似度，其余时候看响应码的异同
                            line_similarity.append(difflib.SequenceMatcher(None, RESPONSES[i].content, RESPONSES[j].content).ratio())
                        else:
                            line_similarity.append(0.0)
                else:
                    line_similarity.append(0.0)
        else:
            for j in range(i):
                if RESPONSES[j] == None:
                    line_similarity.append(1.0)
                else:
                    line_similarity.append(0.0)
        print line_similarity
        SIMILARITY.append(line_similarity)

def compute_the_similarity(req):
    line_similarity = []
    for i in range(len(RESPONSES)):
        if RESPONSES[i] != None:
            if req != None:#双方均有响应的时候才继续计算相似度，否则直接判异同
                if RESPONSES[i].status_code != 200:
                    if req.status_code == RESPONSES[i].status_code:
                        line_similarity.append(1.0)
                    else:
                        line_similarity.append(0.0)
                else:
                    if req.status_code == 200:#响应码均为200才计算内容相似度，其余时候看响应码的异同
                        line_similarity.append(difflib.SequenceMatcher(None, RESPONSES[i].content, req.content).ratio())
                    else:
                        line_similarity.append(0.0)
            else:
                line_similarity.append(0.0)
        else:
            if req == None:
                line_similarity.append(1.0)
            else:
                line_similarity.append(0.0)
    print line_similarity
    TEST_SIMILARITY.append(line_similarity)

def response2file():
    for i in range(len(RESPONSES)):
        if RESPONSES[i] != None:
            f = open('./page/test'+str(i)+'.html','w')
            f.write(RESPONSES[i].content)
            f.close()
    for i in range(len(TEST_RESPONSES)):
        if TEST_RESPONSES[i] != None:
            f = open('./page/Ttest'+str(i)+'.html','w')
            f.write(TEST_RESPONSES[i].content)
            f.close()

def send_test_requests(opt):    
    tree = ET.parse("special.xml")
    root = tree.getroot()
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            keywords = level.findall("keywords")
            test_sen = teststr(urllib.unquote(sentence), opt)
            if test_sen == 0:
                print 'normal'
            elif test_sen == -1:
                return -1
            else:
                print 'banned', sentence
                keywords_text = []
                for keyword in keywords:
                    keywords_text.append(keyword.text)
                for i in range(1,bound + 1):
                    c = combination(keywords_text, i)
                    for k in c:
                        test_keyword = teststr(urllib.unquote(k), opt)
                        if test_keyword == 1:
                            print 'banned' + k
                        else:
                            print TEST_SIMILARITY[-1][0], k
                        
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

def teststr(s, opt):
    query_list, offset, method = find_param_method(opt)
    if method == METHOD_POST:
        req = send_fixed_request(opt, query_list, s, offset, True)
        #print 'sent test request'
        TEST_RESPONSES.append(req)
    elif method == METHOD_GET:
        req = send_fixed_request(opt, query_list, s, offset)
        #print 'sent test request'
        TEST_RESPONSES.append(req)
    else:
        print "Invaild Param:"+opt.param
        return -1
    compute_the_similarity(req)
    if STANDARD_RATIO - TEST_SIMILARITY[-1][0] < ACCEPTABLE_DIFF_RATIO:
        return 0
    else:
        return 1
        
def check_eff(s, opt):
    bound = len(s)
    eff = ""
    while bound > 0:
        start = 0
        end = bound
        left = start
        right = end
        if teststr(eff, opt) == 1:
            break
        while left < right - 1:
            mid = (left + right)/2
            if teststr(s[start:mid]+eff, opt) == 1:
                right = mid
            else:
                left = mid
        if not teststr(s[start:left]+eff, opt) == 1:
            left = right
        eff = s[left - 1] + eff
        bound = left - 1
    return eff
    
def test(opt):
    get_standard_ratio(opt)
    group = get_all_features(opt)
    send_test_requests(opt)
    response2file()
    
def main():
    opt = parse_cmd_args()
    if opt.test:
        test(opt)
        return
    from sys import path
    path.append(MAIN_PATH+'/sqlmap')
    from sqlmap import sqlmain
    print sqlmain(['sqlmap.py', '-u', opt.url, '--identify-waf'])
    get_standard_ratio(opt)
    group = get_all_features(opt)
    response2file()
    print SIMILARITY
if __name__=="__main__":
    main()