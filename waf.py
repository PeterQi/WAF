import requests
from optparse import OptionParser
def main():
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
    (options, args) = parser.parse_args()
    if not options.url or not options.param:
        parser.error("Missing argument for target url or target param. Use '-h' for help.")
    headers = {}
    if options.cookie:
        headers["Cookie"] = options.cookie
    if options.header:
        headers[options.header.split("=")[0]] = options.header.split("=", 1)[1]
    if options.data:
        req = requests.post(options.url,headers=headers,data=options.data)
    else:
        req = requests.get(options.url,headers=headers)

if __name__=="__main__":
    main()