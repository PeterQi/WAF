#coding=utf8
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
import random
import time

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
CJLOCK = threading.Lock()
NORMALLOCK = threading.Lock()
request_num = 0
numlock = threading.Lock()
tmp_share_offset = 0
OFFSETLOCK = threading.Lock()
time1 = time.time()
RULES = []


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
    f = open('./result/'+f_name, 'a')
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
    timeout_period = 60
    if timeout_period > BASE_RESPONSE_TIME * opt.thread:
        timeout_period = BASE_RESPONSE_TIME * opt.thread
    try:
        if post:
            req = requests.post(opt.url,headers = headers, data = query_list, allow_redirects = False, timeout = timeout_period)
            return req
        geturl = urlparse.urlparse(opt.url)
        url = urlparse.urlunparse((geturl.scheme, geturl.netloc, geturl.path, geturl.params, "", geturl.fragment))
        req = requests.get(url,headers = headers, params = query_list, allow_redirects = False, timeout = timeout_period)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
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
        #pool = threadpool.ThreadPool(5)
        reqs = threadpool.makeRequests(threads_feature_payloads,[((),{'opt':opt, 'query_list': query_list, 'param_i':j, 'offset': offset, 'IF_POST': True})for j in range(5)])
        [pool.putRequest(req) for req in reqs]
        try:
            pool.wait()
        except KeyboardInterrupt:
            print 'Stop'
            sys.exit()
        except Exception as e:
            print e
            sys.exit()
    elif method == METHOD_GET:
        #pool = threadpool.ThreadPool(5)
        reqs = threadpool.makeRequests(threads_feature_payloads,[((),{'opt':opt, 'query_list': query_list, 'param_i':j, 'offset': offset, 'IF_POST': False})for j in range(5)])
        [pool.putRequest(req) for req in reqs]
        try:
            pool.wait()
        except KeyboardInterrupt:
            print 'Stop'
            sys.exit()
        except Exception as e:
            print e
            sys.exit()
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
    print SIMILARITY
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
    global tmp_share_offset
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
                        print 'ERROR', sentence
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
                        tmp_share_offset = 0
                        try:
                            #pool = threadpool.ThreadPool(opt.thread)
                            reqs = threadpool.makeRequests(threads_payloads1,[((),{'opt':opt, 'keywords': c, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                            [pool.putRequest(req) for req in reqs]                            
                            pool.wait()
                        except KeyboardInterrupt:
                            print 'You Stop.'
                            sys.exit()
                        except Exception as e:
                            print e
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
    global tmp_share_offset
    global CACHE_EFF
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
                print 'ERROR'
                break
            count1 += 1
            continue
        else:
            print 'BANNED', sentence
            tmp_share_offset = 0
            try:
                #pool = threadpool.ThreadPool(opt.thread)
                reqs = threadpool.makeRequests(threads_payloads2,[((),{'opt':opt, 'keywords': pre_eff, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                [pool.putRequest(req) for req in reqs]
                pool.wait()
            except KeyboardInterrupt:
                print 'You stop.'
                sys.exit()
            except Exception, e:
                print e
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
    global tmp_share_offset
    tree = ET.parse("payload.xml")
    root = tree.getroot()
    #type_pass = 0
    for type in root:
        #tmp_pass = 0
        #if type_pass < 2:
        #    type_pass += 1
        #    continue
        for level in type:
            #if tmp_pass < 5:
            #    tmp_pass += 1
            #    continue
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
                        print 'ERROR', sentence
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
                        tmp_share_offset = 0
                        try:
                            reqs = threadpool.makeRequests(threads_payloads2,[((),{'opt':opt, 'keywords': c, 'test_sen': test_sen})for j in range(opt.thread)], handle_results)
                            [pool.putRequest(req) for req in reqs]
                            pool.wait()
                        except KeyboardInterrupt:
                            print 'You stop.'
                            sys.exit()
                        except Exception , e:
                            print Exception, e
                            sys.exit()
                        if len(CACHE_EFF) > 0:
                            banned_eff = True
                            ALL_BANNED_EFFECTIVE_VECTOR += CACHE_EFF
                        CACHE_EFF = []
                        print ALL_BANNED_EFFECTIVE_VECTOR
                    if not banned_eff:
                        print 'not right'
                        find_exact = check_eff(sentence, opt, test_sen)
                        ALL_BANNED_EFFECTIVE_VECTOR.append(find_exact)
                break
            print request_num, 
            time2 = time.time()
            print_time(time2-time1)

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
    CJLOCK.acquire()
    RESPONSES.append(req)
    CJLOCK.release()
        
def threads_payloads1(opt, keywords, test_sen):#for special.xml
    global tmp_share_offset
    banned_eff = []
    l = len(keywords)
    OFFSETLOCK.acquire()
    k = tmp_share_offset
    tmp_share_offset += 1
    OFFSETLOCK.release()
    while k < l:
        count = 0
        if urllib.unquote(keywords[k]) in NORMAL:
            OFFSETLOCK.acquire()
            k = tmp_share_offset
            tmp_share_offset += 1
            OFFSETLOCK.release()
            continue
        while True:
            try:
                test_keyword = teststr(urllib.unquote(keywords[k]), opt)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                print e
                sys.exit()
            if test_keyword == test_sen:
                print 'BANNED', keywords[k]
                banned_eff.append(urllib.unquote(keywords[k]))
            elif test_keyword < 0:
                if count >= 5:
                    print 'ERROR', keywords[k]
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
        OFFSETLOCK.acquire()
        k = tmp_share_offset
        tmp_share_offset += 1
        OFFSETLOCK.release()
    if len(banned_eff) == 0:
        return banned_eff
    else:
        find_exact_eff = []
        for b in banned_eff:
            if len(b) == 1:
                find_exact_eff.append(b)
            else:
                find_exact_eff.append(check_eff(b, opt, test_sen))
        return find_exact_eff

def threads_payloads2(opt, keywords, test_sen):#for payload.xml
    global tmp_share_offset
    banned_eff = []
    l = len(keywords)
    OFFSETLOCK.acquire()
    k = tmp_share_offset
    tmp_share_offset += 1
    OFFSETLOCK.release()
    while k < l:
        count = 0
        for e in ALL_BANNED_EFFECTIVE_VECTOR:
            keywords[k] = keywords[k].replace(e, "")
        if len(keywords[k])==0:
            OFFSETLOCK.acquire()
            k = tmp_share_offset
            tmp_share_offset += 1
            OFFSETLOCK.release()
            continue
        if keywords[k] in NORMAL:
            OFFSETLOCK.acquire()
            k = tmp_share_offset
            tmp_share_offset += 1
            OFFSETLOCK.release()
            continue
        while True:
            test_keyword = teststr(keywords[k], opt)
            if test_keyword == test_sen:
                print 'BANNED', keywords[k]
                find_exact = check_eff(keywords[k], opt, test_sen)
                banned_eff.append(find_exact)
            elif test_keyword < 0:
                if count >= 5:
                    print 'ERROR', keywords[k]
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
        OFFSETLOCK.acquire()
        k = tmp_share_offset
        tmp_share_offset += 1
        OFFSETLOCK.release()

    return banned_eff

def handle_results(request, result):
    global CACHE_EFF
    #print request.requestID,
    CJLOCK.acquire()
    CACHE_EFF += result
    CJLOCK.release()

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
        try:
            req = send_fixed_request(opt, query_list, s, offset, True)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print e
            raise Exception
        TEST_RESPONSES.append(req)
    elif method == METHOD_GET:
        try:
            req = send_fixed_request(opt, query_list, s, offset)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print e
            raise Exception
        TEST_RESPONSES.append(req)
    else:
        print "Invaild Param:"+opt.param
        return -2
    compute_the_similarity(req, opt)
    for i in range(len(RESPONSES)):
        if STANDARD_RATIO - TEST_SIMILARITY[-1][i] < ACCEPTABLE_DIFF_RATIO:
            print '\x08.',
            return i
    print '\x08.',
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
                        print 'ERROR'
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
                        print 'ERROR'
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
    except Exception, e:
        print e
        sys.exit()

def teststr_reg(s, opt):
    if s in NORMAL:
        return False
    count = 0
    while True:
        class_num = teststr(s, opt)
        if class_num < 0:
            if count >= 5:
                print 'ERROR'
                return False
            count += 1
            continue
        elif class_num == 0:
            return False
        else:
            return True
        
def case_switch(st):
    C_st = ""
    flag = False
    for c in st:
        ascii = ord(c)
        if ascii >= 65 and ascii <= 90:
            flag = True
            if random.randint(0,1):
                C_st += c.lower()
            else:
                C_st += c
        elif ascii >= 97 and ascii <= 122:
            flag = True
            if random.randint(0,1):
                C_st += c.upper()
            else:
                C_st += c
        else:
            C_st += c
    if not flag:
        return st
    if C_st == st:
        C_st = case_switch(st)
    return C_st
        
def rand_chr(chrs, banned = ""):
    if len(chrs) == 1:
        return chr(chrs[0])
    elif len(chrs) == 0:
        return ''
    c = chr(chrs[random.randint(0, len(chrs)-1)])
    if c == banned.lower() or c == banned.upper():
        c = rand_chr(chrs, banned)
    return c
        
def replace_chr(st, offset, eff):
    w_chrs = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
    WS_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    sN_chrs = [9, 11, 12, 13, 32]
    dot_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    d_chrs = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    D_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    W_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    s_chrs = [9, 10, 11, 12, 13, 32]
    S_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    if offset < 0 or offset >= len(st):
        return ''
    test_st = copy.copy(st)
    test_st = test_st[:offset] + chr(10) + test_st[offset+1:]
    #print test_st
    if st[offset] == test_st[offset] or teststr_reg(test_st, eff):
        sec_test = rand_chr(w_chrs, st[offset])
        test_st = test_st[:offset] + sec_test + test_st[offset+1:]
        if teststr_reg(test_st, eff):
            return '\D'
        else:
            trd_test = rand_chr(WS_chrs, st[offset])
            test_st = test_st[:offset] + trd_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                return '\W'
            else:
                return '\s'
    else:
        sec_test = rand_chr(w_chrs, st[offset])
        test_st = test_st[:offset] + sec_test + test_st[offset+1:]
        if teststr_reg(test_st, eff):
            trd_test = rand_chr(WS_chrs, st[offset])
            test_st = test_st[:offset] + trd_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                fth_test = rand_chr(sN_chrs, st[offset])
                test_st = test_st[:offset] + fth_test + test_st[offset+1:]
                if teststr_reg(test_st, eff):
                    return '.'
                else:
                    return '\S'
            else:
                return '\w'
        else:
            d_test = rand_chr(d_chrs, st[offset])
            test_st = test_st[:offset] + d_test + test_st[offset+1:]
            if teststr_reg(test_st, eff):
                return '\d'
            else:
                return regular_special(st[offset])
                   
def insert_chr(st, offset, eff):
    w_chrs = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]
    WS_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    sN_chrs = [9, 11, 12, 13, 32]
    dot_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    d_chrs = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
    D_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    W_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 92, 93, 94, 96, 123, 124, 125, 126, 127]
    s_chrs = [9, 10, 11, 12, 13, 32]
    S_chrs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67,68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
    if offset <= 0 or offset >= len(st):
        return ''
    pattern = ''
    test_st = copy.copy(st)
    test_st = st[:offset] + chr(10) + st[offset:]
    if teststr_reg(test_st, eff):
        sec_test = rand_chr(w_chrs)
        test_st = st[:offset] + sec_test + st[offset:]
        if teststr_reg(test_st, eff):
            pattern = '\D'
            test_st = st[:offset]
            for i in range(10):
                multi_test = rand_chr(D_chrs)
                test_st += multi_test
            test_st += st[offset:]
            if teststr_reg(test_st, eff):
                return pattern+'*'
            else:
                return pattern+'?'
        else:
            trd_test = rand_chr(WS_chrs)
            test_st = st[:offset] + trd_test + st[offset:]
            if teststr_reg(test_st, eff):
                pattern = '\W'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(W_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern+'?'
            else:
                pattern = '\s'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(s_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern+'?'
    else:
        sec_test = rand_chr(w_chrs)
        test_st = st[:offset] + sec_test + st[offset:]
        if teststr_reg(test_st, eff):
            trd_test = rand_chr(WS_chrs)
            test_st = st[:offset] + trd_test + st[offset:]
            if teststr_reg(test_st, eff):
                fth_test = rand_chr(sN_chrs)
                test_st = st[:offset] + fth_test + st[offset:]
                if teststr_reg(test_st, eff):
                    pattern = '.'
                    test_st = st[:offset]
                    for i in range(10):
                        multi_test = rand_chr(dot_chrs)
                        test_st += multi_test
                    test_st += st[offset:]
                    if teststr_reg(test_st, eff):
                        return pattern+'*'
                    else:
                        return pattern+'?'
                else:
                    pattern = '\S'
                    test_st = st[:offset]
                    for i in range(10):
                        multi_test = rand_chr(S_chrs)
                        test_st += multi_test
                    test_st += st[offset:]
                    if teststr_reg(test_st, eff):
                        return pattern+'*'
                    else:
                        return pattern+'?'
                    
            else:
                pattern = '\w'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(w_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern+'?'
        else:
            d_test = rand_chr(d_chrs)
            test_st = st[:offset] + d_test + st[offset:]
            if teststr_reg(test_st, eff):
                pattern = '\d'
                test_st = st[:offset]
                for i in range(10):
                    multi_test = rand_chr(d_chrs)
                    test_st += multi_test
                test_st += st[offset:]
                if teststr_reg(test_st, eff):
                    return pattern+'*'
                else:
                    return pattern+'?'
            else:
                return ''
    
def case_chr(st, eff):
    test_st = case_switch(st)
    if teststr_reg(test_st, eff):
        return True
    else:
        return False
    
def get_reg(st, opt):
    global RULE_TMP
    RULE_TMP = ['' for i in range(len(st)*2)]
    reqs = threadpool.makeRequests(replace_chr,[((),{'st':st, 'offset': i, 'eff': opt})for i in range(len(st))], handle_results2)
    reqs += threadpool.makeRequests(insert_chr,[((),{'st':st, 'offset': i, 'eff': opt})for i in range(len(st))], handle_results3)
    [pool.putRequest(req) for req in reqs]
    try:
        pool.wait()
    except KeyboardInterrupt:
        print 'Stop'
        sys.exit()
    except Exception as e:
        print e
        sys.exit()
    result = ''.join(RULE_TMP)
    if case_chr(st, opt):
        result = '(?i)'+result
    print result
    return result
    
def handle_results2(request, result):
    global RULE_TMP
    RULE_TMP[request.kwds['offset']*2+1] = result
    
def handle_results3(request, result):
    global RULE_TMP
    RULE_TMP[request.kwds['offset']*2] = result

def regular_match(st, rule):
    data = re.search(rule, st)
    if data == None:
        return False
    else:
        return True
    
def rules_get(opt):
    global RULES
    for b in ALL_BANNED_EFFECTIVE_VECTOR:
        flag = False
        for r in RULES:
            if len(r) == 0:
                continue
            if regular_match(b, r):
                flag = True
                break
        if not flag:
            RULES.append(get_reg(b, opt))
        print b
            
def regular_special(ch):
    if ch in '$()*+.[]?\\{}|':
        return '\\' + ch
    else:
        return ch
    
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
    for i in RULES:
        f.write(i)
        f.write('\n')
    f.write('Total Requests num:'+str(request_num)+'\n')
    f.close()

def print_time(t):
    sec = int(t) % 60
    t = int(t) / 60
    min = t % 60
    t /= 60
    hour = t % 24
    #t /= 24
    #day = t
    ti = str(hour)+'h'+str(min)+'m'+str(sec)+'s'
    print ti
    return ti

def banned_effective_vector_clear():
    global ALL_BANNED_EFFECTIVE_VECTOR
    tmp_vectors = []
    for i in ALL_BANNED_EFFECTIVE_VECTOR:
        if i not in tmp_vectors:
            tmp_vectors.append(i)
    ALL_BANNED_EFFECTIVE_VECTOR = tmp_vectors
    
def test(opt):
    global pool
    global ALL_BANNED_EFFECTIVE_VECTOR
    opt = parse_cmd_args()
    if not opt.thread:
        opt.thread = 5
    else:
        opt.thread = int(opt.thread)
    get_standard_ratio(opt)
    pool = threadpool.ThreadPool(opt.thread)
    group = get_all_features(opt)
    if group <= 1:
        print "Didn't find WAF Product"
        return 0
    ALL_BANNED_EFFECTIVE_VECTOR=['', 'onload', 'onblur', 'onfocus', 'onclick', 'onabort', 'onselect', 'onsubmit', 'onkeydown', 'onmouseout', 'onmousedown', 'onmouseover', '<script', '<img', 'javascript', 'document.cookie', '<frame']
    rules_get(opt)
    response2file2(opt)
    f_name = urlparse.urlparse(opt.url).netloc
    f = open('./result/'+f_name, 'a')
    time2 = time.time()
    f.write("Total time:"+print_time(time2-time1)+'\n')
    f.close()
    
def main():
    global pool
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
    get_standard_ratio(opt)
    pool = threadpool.ThreadPool(opt.thread)
    group = get_all_features(opt)
    if group <= 1:
        print "Didn't find WAF Product"
        return 0
    pre_test_payloads(opt)
    send_test_requests(opt)
    send_payloads(opt)
    banned_effective_vector_clear()
    rules_get(opt)
    response2file2(opt)
    sqlmap_detect = sqlmain(['sqlmap.py', '-u', opt.url, '--identify-waf'])
    f_name = urlparse.urlparse(opt.url).netloc
    f = open('./result/'+f_name, 'a')
    f.write('WAF PRODUCT:')
    for s in sqlmap_detect:
        f.write(s+'\n')
    time2 = time.time()
    f.write("Total time:"+print_time(time2-time1)+'\n')
    f.close()
    
if __name__=="__main__":
    main()
