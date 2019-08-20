import time
import re
import urllib
from collections import defaultdict
from pprint import pprint
import itertools
from operator import itemgetter
from utils import tail


class SQLi:
    type = "SQLi"

    def __init__(self, datetime, host, request_method, payload, useragent):
        self.datetime = datetime
        self.host = host
        self.request_method = request_method
        self.payload = payload
        self.useragent = useragent


class XSS:
    type = "XSS"

    def __init__(self, datetime, host, request_method, payload, useragent):
        self.datetime = datetime
        self.host = host
        self.request_method = request_method
        self.payload = payload
        self.useragent = useragent


def decode_html(encoded):
    return urllib.unquote(encoded)


def encode_html(decoded):
    return urllib.quote(decoded)


# def tail(logfile):
#     logfile.seek(0, 2)
#     while True:
#         line = logfile.readline()
#         if not line:
#             time.sleep(0.1)
#             continue
#         yield line


def parsing(loglines):
    logpats = r'(\S+) (\S+) (\S+) \[(.*?)\] ' \
        r'"(\S+) (\S+) (\S+)" (\S+) (\S+) (\S+) (\S+) (\S+)'
    logpat = re.compile(logpats)
    groups = (logpat.match(line) for line in loglines)
    tuples = (g.groups() for g in groups if g)

    colnames = ('host', 'location', 'user', 'datetime',
                'method', 'request', 'protocol', 'status', 'bytes', 'referer', 'uagent')
    log = (dict(zip(colnames, t)) for t in tuples)
    log = mapp(log, "status", int)
    log = mapp(log, "bytes", lambda s: int(s) if s != '-' else 0)
    return log

# based on mapp function from https://github.com/pobyzaarif/hansipy


def mapp(dictseq, name, func):
    for d in dictseq:
        d[name] = func(d[name])
        yield d


def analyze(logs):
    xss = ['%3C', '<img', '<a href', '<body',
           '<script', '<b', '<h', '<marquee', '<svg/onload=']
    sqli = ['%27', '--', '%3B', 'exec', 'union+', 'union*',
            'system\(', 'eval(', 'group_concat', 'column_name', 'order by', 'insert into', 'load_file', '@version']

    # v structure in tuple format
    # (<host>, <datetime>, <host|ip>, <http_request_method>, <request_line>)

    for r in logs:
        for s in xss:
            if s in r['request']:
                # v='XSS', r['datetime'],r['host'],r['method'],r['request']
                v = XSS(r['datetime'], r['host'], r['method'],
                        r['request'], r['uagent'])
                yield v

        for s in sqli:
            if s in r['request']:
                # v='SQLi', r['datetime'],r['host'],r['method'],r['request']
                v = SQLi(r['datetime'], r['host'], r['method'], r['request'], r['uagent'])
                print("[!] SQLi detected: %s" % r['request'])
                yield v

        if 400 <= r['status'] <= 500:
            v = 'ERR_4xx', r['datetime'], r['host'], r['method'], r['request']
            yield v

        elif r['status'] >= 500:
            v = 'ERR_5xx', r['datetime'], r['host'], r['method'], r['request']
            yield v

        else:
            pass


def threat_grouping(arrays):
    try:
        v = defaultdict(list)
        for i in arrays:
            if i.type == 'XSS':
                v['XSS'].append(i)
            if i.type == 'SQLi':
                v['SQLi'].append(i)
    except Exception as e:
        pass

    return v

if __name__ == '__main__':
    logfile = open("./samples/GET.csv", "r")
    loglines = tail(logfile)

    logs = parsing(loglines)
    t_grouped = threat_grouping(analyze(logs))

    for g in t_grouped['XSS']:
        print(vars(g))
    
    for g in t_grouped['SQLi']:
        print(vars(g))

    # print grouped

    # for i in grouped['SQLi']:
    #         print i
    # for i in groupd:
    #     print i.values()
    # for i in result:
    # 	print type(i.payload), i.useragent
