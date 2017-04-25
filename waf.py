#coding=utf-8
import requests
from optparse import OptionParser
import xml.etree.ElementTree as ET
import os
import difflib
import urlparse
import urllib
import sys
import copy
import thread
import threading
import threadpool
import re

MAIN_PATH = os.path.abspath('.')
STANDARD_RATIO = 0
RESPONSES = []
TEST_RESPONSES = []
SIMILARITY = []
TEST_SIMILARITY = []
ALL_BANNED_EFFECTIVE_VECTOR = []
METHOD_POST = 2
METHOD_GET = 1
NOT_FOUND = 0
ACCEPTABLE_DIFF_RATIO = 0.05
BASE_RESPONSE_TIME = 60.0
CACHE_EFF = []
NORMAL = []
cjlock = threading.Lock()
NORMALLOCK = threading.Lock()
request_num = 0
numlock = threading.Lock()

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
    parser.add_option("-t", "--thread", dest="thread", help="set multiple thread num, default 5")
    parser.add_option("-r", dest="regular", help="set regular expression to compare")
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
    except KeyboardInterrupt:
        print 'You Stop.'
        sys.exit()
    except Exception, e:
        print Exception, ':', e
        sys.exit()
    
def get_standard_ratio(opt):
    global STANDARD_RATIO
    global BASE_RESPONSE_TIME
    global request_num
    print 'Original request is responsing'
    req1 = first_request(opt)
    RESPONSES.append(req1)
    req2 = first_request(opt)
    request_num += 2
    BASE_RESPONSE_TIME = (req1.elapsed.microseconds/1000000.0 + req1.elapsed.seconds + req2.elapsed.microseconds/1000000.0 + req2.elapsed.seconds)/2.0
    print 'Base response time:' + str(BASE_RESPONSE_TIME) + 's'
    print 'Top similarity:', 
    #STANDARD_RATIO = difflib.SequenceMatcher(None, req1.content, req2.content).ratio()
    STANDARD_RATIO = diff_ratio(opt, req1.content, req2.content)
    print STANDARD_RATIO
    f_name = urlparse.urlparse(opt.url).netloc
    f = open('./result/'+f_name, 'w')
    f.write('Base response time:' + str(BASE_RESPONSE_TIME) + 's\n')
    f.write('Top similarity:'+str(STANDARD_RATIO)+'\n')
    f.close()
    return STANDARD_RATIO

def send_fixed_request(opt, query_list, str, offset, post = False):
    global request_num
    headers = {}
    query_list[offset] = (opt.param, str)
    if opt.cookie:
        headers["Cookie"] = opt.cookie
    if opt.header:
        headers[opt.header.split("=")[0]] = options.header.split("=", 1)[1]
    numlock.acquire()
    request_num += 1
    numlock.release()
    try:
        if post:
            req = requests.post(opt.url,headers = headers, data = query_list, allow_redirects = False, timeout = BASE_RESPONSE_TIME*30)
            return req
        geturl = urlparse.urlparse(opt.url)
        url = urlparse.urlunparse((geturl.scheme, geturl.netloc, geturl.path, geturl.params, "", geturl.fragment))
        req = requests.get(url,headers = headers, params = query_list, allow_redirects = False, timeout = BASE_RESPONSE_TIME*3)
    except KeyboardInterrupt:
        print 'You Stop.'
        sys.exit()
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
    query_list, offset, method = find_param_method(opt)
    
    print 'sending mixed requests'
    if method == METHOD_POST:
        pool = threadpool.ThreadPool(5)
        reqs = threadpool.makeRequests(threads_feature_payloads,[((),{'opt':opt, 'query_list': query_list, 'param_i':j, 'offset': offset, 'IF_POST': True})for j in range(5)])
        [pool.putRequest(req) for req in reqs]
        pool.wait()
    elif method == METHOD_GET:
        pool = threadpool.ThreadPool(5)
        reqs = threadpool.makeRequests(threads_feature_payloads,[((),{'opt':opt, 'query_list': query_list, 'param_i':j, 'offset': offset, 'IF_POST': False})for j in range(5)])
        [pool.putRequest(req) for req in reqs]
        pool.wait()
    else:
        print "Invaild Param:"+opt.param
        return -1
    print 'start computing similarity...'
    compute_similarity(opt)
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

def diff_ratio(opt, str1, str2):
    if not opt.regular:
        return difflib.SequenceMatcher(None, str1, str2).ratio()
    else:
        pattern = re.compile(opt.regular)
        o1 = pattern.search(str1)
        s1 = ''
        if o1 != None:
            p1 = o1.groups()
            if len(p1) > 0:
                s1 = p1[0]
            else:
                s1 = o1.group()
        o2 = pattern.search(str2)
        s2 = ''
        if o2 != None:
            p2 = o2.groups()
            if len(p2) > 0:
                s2 = p2[0]
            else:
                s2 = o2.group()
        return difflib.SequenceMatcher(None, s1, s2).ratio()

def compute_similarity(opt):
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
                            line_similarity.append(diff_ratio(opt, RESPONSES[i].content, RESPONSES[j].content))
                            #line_similarity.append(difflib.SequenceMatcher(None, RESPONSES[i].content, RESPONSES[j].content).ratio())
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

def compute_the_similarity(req, opt):
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
                        line_similarity.append(diff_ratio(opt, RESPONSES[i].content, req.content))
                        #line_similarity.append(difflib.SequenceMatcher(None, RESPONSES[i].content, req.content).ratio())
                    else:
                        line_similarity.append(0.0)
            else:
                line_similarity.append(0.0)
        else:
            if req == None:
                line_similarity.append(1.0)
            else:
                line_similarity.append(0.0)
    #print line_similarity
    TEST_SIMILARITY.append(line_similarity)

def send_test_requests(opt):
    global ALL_BANNED_EFFECTIVE_VECTOR
    global CACHE_EFF
    tree = ET.parse("special.xml")
    root = tree.getroot()
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            keywords = level.findall("keywords")
            count1 = 0
            while True:
                test_sen = teststr(urllib.unquote(sentence), opt)
                if test_sen == 0:
                    print 'NORMAL', sentence
                elif test_sen == -2:
                    return -1
                elif test_sen < 0:
                    if count1 >= 5:
                        print 'error', sentence
                        break
                    count1 += 1
                    continue
                else:
                    print 'BANNED', sentence
                    keywords_text = []
                    for keyword in keywords:
                        keywords_text.append(keyword.text)
                    banned_eff = []
                    for i in range(1,bound + 1):
                        c = combination(keywords_text, i)
                        num = len(c)
                        try:
                            pool = threadpool.ThreadPool(opt.thread)
                            reqs = threadpool.makeRequests(threads_payloads1,[((),{'opt':opt, 'keywords': c, 'offset':j, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                            [pool.putRequest(req) for req in reqs]
                            pool.wait()
                        except KeyboardInterrupt:
                            print 'You Stop.'
                            sys.exit()
                        
                        if len(CACHE_EFF) == 0:
                            find_exact = check_eff(urllib.unquote(sentence), opt, test_sen)
                            ALL_BANNED_EFFECTIVE_VECTOR.append(find_exact)
                        else:
                            ALL_BANNED_EFFECTIVE_VECTOR += CACHE_EFF
                        CACHE_EFF = []
                        print ALL_BANNED_EFFECTIVE_VECTOR
                break
                
def pre_test_payloads(opt):
    global ALL_BANNED_EFFECTIVE_VECTOR
    tree = ET.parse("payload.xml")
    root = tree.getroot()
    count = 0
    al_num = 0
    max_len = 0
    times = 0
    eff = []
    pre_eff = []
    sentence_pre = ""
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
                            sentence_pre += e
                keywords_text.append(keyword.text)
            eff += keywords_text
    count1 = 0
    sentence = sentence_pre
    while True:
        test_sen = teststr(sentence, opt)
        if test_sen == 0:
            print 'NORMAL', sentence
        elif test_sen == -2:
            return -1
        elif test_sen < 0:
            if count1 >= 5:
                print 'error'
                break
            count1 += 1
            continue
        else:
            print 'BANNED', sentence
            try:
                pool = threadpool.ThreadPool(opt.thread)
                reqs = threadpool.makeRequests(threads_payloads2,[((),{'opt':opt, 'keywords': pre_eff, 'offset':j, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                [pool.putRequest(req) for req in reqs]
                pool.wait()
            except KeyboardInterrupt:
                print 'You stop.'
                sys.exit()
            if len(CACHE_EFF) == 0:
                find_exact = check_eff(sentence, opt, test_sen)
                ALL_BANNED_EFFECTIVE_VECTOR.append(find_exact)
            else:
                ALL_BANNED_EFFECTIVE_VECTOR += CACHE_EFF
            CACHE_EFF = []
            print ALL_BANNED_EFFECTIVE_VECTOR
        break

def send_payloads(opt):
    global ALL_BANNED_EFFECTIVE_VECTOR
    global CACHE_EFF
    tree = ET.parse("payload.xml")
    root = tree.getroot()
    for type in root:
        for level in type:
            bound = int(level.attrib['bound'])
            sentence = level.find("sentences").text
            keywords = level.findall("keywords")
            count1 = 0
            while True:
                test_sen = teststr(sentence, opt)
                if test_sen == 0:
                    print 'NORMAL', sentence
                elif test_sen == -2:
                    return -1
                elif test_sen < 0:
                    if count1 >= 5:
                        print 'error', sentence
                        break
                    count1 += 1
                    continue
                else:
                    print 'BANNED', sentence
                    keywords_text = []
                    for keyword in keywords:
                        keywords_text.append(keyword.text)
                    banned_eff = False
                    for i in range(1,bound + 1):
                        c = combination(keywords_text, i)
                        try:
                            pool = threadpool.ThreadPool(opt.thread)
                            reqs = threadpool.makeRequests(threads_payloads2,[((),{'opt':opt, 'keywords': c, 'offset':j, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                            [pool.putRequest(req) for req in reqs]
                            pool.wait()
                        except KeyboardInterrupt:
                            print 'You stop.'
                            sys.exit()
                        if len(CACHE_EFF) > 0:
                            banned_eff = True
                            ALL_BANNED_EFFECTIVE_VECTOR += CACHE_EFF
                        CACHE_EFF = []
                        print ALL_BANNED_EFFECTIVE_VECTOR
                    if not banned_eff:
                        find_exact = check_eff(sentence, opt, test_sen)
                        ALL_BANNED_EFFECTIVE_VECTOR.append(find_exact)
                break
            print request_num

def threads_feature_payloads(opt, query_list, param_i, offset, IF_POST):
    param = ''
    tmp_query_list = copy.copy(query_list)
    if param_i == 0:
        pass
    elif param_i == 1:
        param = 100
    elif param_i == 2:
        param = "hello"
    elif param_i == 3:
        param = "!\"$%&\\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r#\x0b\x0c"
    elif param_i == 4:
        param = "AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(\"XSS\")</script>',table_name FROM information_schema.tables WHERE 2>1--/**/; EXEC xp_cmdshell('cat ../../../etc/passwd')#"
    req = send_fixed_request(opt, tmp_query_list, param, offset, IF_POST)
    cjlock.acquire()
    RESPONSES.append(req)
    cjlock.release()
        
def threads_payloads1(opt, keywords, offset, test_sen):#for special.xml
    banned_eff = []
    l = len(keywords)
    for k in range(offset, l, opt.thread):
        count = 0
        if urllib.unquote(keywords[k]) in NORMAL:
            continue
        while True:
            test_keyword = teststr(urllib.unquote(keywords[k]), opt)
            if test_keyword == test_sen:
                print 'BANNED', keywords[k]
                banned_eff.append(urllib.unquote(keywords[k]))
            elif test_keyword < 0:
                if count >= 5:
                    print 'error', keywords[k]
                    break
                count += 1
                continue
            else:
                NORMALLOCK.acquire()
                NORMAL.append(urllib.unquote(keywords[k]))
                NORMALLOCK.release()
                #print 'NORMAL', keywords[k]
                
            count = 0
            break
    if len(banned_eff) == 0:
        return offset, banned_eff
    else:
        find_exact_eff = []
        for b in banned_eff:
            if len(b) == 1:
                find_exact_eff.append(b)
            else:
                find_exact_eff.append(check_eff(b, opt, test_sen))
        return offset, find_exact_eff

def threads_payloads2(opt, keywords, offset, test_sen):#for payload.xml
    banned_eff = []
    l = len(keywords)
    for k in range(offset, l, opt.thread):
        count = 0
        for e in ALL_BANNED_EFFECTIVE_VECTOR:
            keywords[k] = keywords[k].replace(e, "")
        if len(keywords[k])==0:
            continue
        if keywords[k] in NORMAL:
            continue
        while True:
            test_keyword = teststr(keywords[k], opt)
            if test_keyword == test_sen:
                print 'BANNED', keywords[k]
                find_exact = check_eff(keywords[k], opt, test_sen)
                banned_eff.append(find_exact)
            elif test_keyword < 0:
                if count >= 5:
                    print 'error', keywords[k]
                    break
                count += 1
                continue
            else:
                NORMALLOCK.acquire()
                NORMAL.append(keywords[k])
                NORMALLOCK.release()
                #print 'NORMAL', keywords[k], len(NORMAL)
            count = 0
            break
    return offset, banned_eff
        
def handle_results(request, result):
    global CACHE_EFF
    cjlock.acquire()
    CACHE_EFF += result[1]
    cjlock.release()

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
        TEST_RESPONSES.append(req)
    elif method == METHOD_GET:
        req = send_fixed_request(opt, query_list, s, offset)
        TEST_RESPONSES.append(req)
    else:
        print "Invaild Param:"+opt.param
        return -2
    compute_the_similarity(req, opt)
    for i in range(len(RESPONSES)):
        if STANDARD_RATIO - TEST_SIMILARITY[-1][i] < ACCEPTABLE_DIFF_RATIO:
            return i
    return -1
        
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

def teststr_del(s, eff):
    s1 = copy.copy(s)
    eff1 = copy.copy(eff)
    i = 0
    j = 0
    len1 = len(eff)
    len2 = len(s)
    flag = False
    while i < len1 and j < len2:
        if eff1[i] == s1[j]:
            i += 1
            s1 = s1[:j]+s1[j+1:]
            len2 -= 1
            continue
        j += 1
    if i >= len1:
        return True, s1
    else:
        return False, s1

def check_eff(s, opt, sen_flag):
    bound = len(s)
    eff = ""
    try:
        while bound > 0:
            start = 0
            end = bound
            left = start
            right = end
            if eff not in NORMAL and len(eff) > 0:
                if teststr(eff, opt) == sen_flag:
                    break
                else:
                    NORMALLOCK.acquire()
                    NORMAL.append(eff)
                    NORMALLOCK.release()
            count = 0
            while left < right - 1:
                mid = (left + right)/2
                if s[start:mid]+eff in NORMAL:
                    left = mid
                    continue
                res = teststr(s[start:mid]+eff, opt)
                if  res == sen_flag:
                    right = mid
                elif res < 0:
                    if count >= 5:
                        print 'error'
                        return ""
                    count += 1
                    continue
                else:
                    NORMALLOCK.acquire()
                    NORMAL.append(s[start:mid]+eff)
                    NORMALLOCK.release()
                    left = mid
                count = 0
            count = 0
            while True:
                if s[start:left]+eff in NORMAL:
                    left = right
                    break
                res = teststr(s[start:left]+eff, opt)
                if res < 0:
                    if count >= 5:
                        print 'error'
                        return ""
                    count += 1
                    continue
                if res != sen_flag:
                    left = right
                break
            eff = s[left - 1] + eff
            bound = left - 1
        return eff
    except KeyboardInterrupt:
        print 'You stop.'
        sys.exit()
    
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
            
def response2file2(opt):
    f_name = urlparse.urlparse(opt.url).netloc
    f = open('./result/'+f_name, 'a')
    for i in ALL_BANNED_EFFECTIVE_VECTOR:
        f.write(i)
        f.write('\n')
    f.write('Total Requests num:'+str(request_num)+'\n')
    f.close()
    
def banned_effective_vector_clear():
    global ALL_BANNED_EFFECTIVE_VECTOR
    tmp_vectors = []
    for i in ALL_BANNED_EFFECTIVE_VECTOR:
        if i not in tmp_vectors:
            tmp_vectors.append(i)
    ALL_BANNED_EFFECTIVE_VECTOR = tmp_vectors
    
def test(opt):
    get_standard_ratio(opt)
    group = get_all_features(opt)
    pre_test_payloads(opt)
    send_test_requests(opt)
    send_payloads(opt)
    banned_effective_vector_clear()
    response2file2(opt)
    
def main():
    opt = parse_cmd_args()
    if not opt.thread:
        opt.thread = 5
    else:
        opt.thread = int(opt.thread)
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