#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Overview
========

A small but useful tool to parser mysql slow query
contact: qingqibai@gmail.com

Usage summary
=============

You need to install python-sqlparse to run this tool
you may:
    apt-get install python-sqlparse
or:
    pip install sqlparse

How to use mysql-slow-query-parser to parser slow query::
    You can get help with ./parser -h or ./parser --help
    ./parser -f /var/log/mysql/slow-query.log (this will parser the last two hours slow query)
    tail -n2000 /var/log/mysql/slow-query.log|./parser (this will parser the lastest 2000 lines slow query)
    ./parser -f /var/log/mysql/slow-query.log -b'130811 13' -e'130811 15' -sa
    ./parser -f /var/log/mysql/slow-query.log -b'130818' -e'130809' -sc
    -f or --log_file: the mysql slow query log you want to parser
    -b or --begin-time: the begin time to parse, if not set, it will start at two hours ago
    -e or --end-time: the end time to parse, if not set, it will parse to now
    -t or --tmp-file: the tmp file, default /tmp/mysql-slow-query-parse
    -s or --sort: sort method, c: sort by count desc, t:sort by averger query time desc,
                  a: sort by c*t desc; default c
"""

import sys
import re
import sqlparse
import argparse
from datetime import datetime, timedelta
from util import SlowQueryLog
from sqlparse.tokens import Token

class SlowQueryParser(object):

    def __init__(self, start_time, end_time, log_file, tmp_file, sort):
        self.start_time = start_time
        self.end_time = end_time
        self.log_file = log_file
        self.tmp_file = tmp_file
        self.sort = sort
        if not self.start_time:
            self.start_time = datetime.strftime(datetime.now() - timedelta(seconds=7200), '%y%m%d %H:')
        if not self.end_time:
            self.end_time = datetime.strftime(datetime.now() - timedelta(seconds=7200), '%y%m%d %H:')

    def pattern(self, sql):
        res = sqlparse.parse(sql)
        if len(res) != 1:
            raise ValueError("Invalid sql: %s" % sql)
        stmt = res[0]
        tokens_queue = [stmt.tokens]
        while len(tokens_queue) > 0:
            tokens = tokens_queue.pop(0)
            for t in tokens:
                if hasattr(t, 'tokens'):
                    tokens_queue.append(t.tokens)
                else:
                    if self.is_atomic_type(t):
                        t.value = '?'
        return self.optimize(unicode(stmt))

    def is_atomic_type(self, token):
        t = self.token_type(token)
        if t == Token.Keyword and token.value == 'NULL':
            return True

        return t in {
                Token.Literal.Number.Integer, 
                Token.Literal.Number.Float, 
                Token.Literal.String.Single, 
                Token.Literal.String.Symbol
                }

    def token_type(self, token):
        if hasattr(token, 'ttype'):
            return token.ttype
        return None

    def optimize(self, pattern):
        return re.sub("in\s+\([\?\s,]+\)", 'IN (?, ?)', pattern, flags=re.IGNORECASE)

    def strip_non_ascii(self, string):
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)

    def remove_use_and_ts(self, sql):
        clean_patterns = ['use ', 'SET timestamp']
        for p in clean_patterns:
            if sql.startswith(p):
                sql = sql[sql.find(';') + 1:].strip()
        return sql.strip(';')

    def shorter(self, sql):
        sql = re.sub('(\d+\s*,\s*){32,}', '123321, 123321', sql)
        sql = re.sub("('\d+'\s*,\s*){32,}", "'123321', '123321'", sql)
        return sql

    def clean(self, sql):
        sql = self.strip_non_ascii(sql)
        sql = self.remove_use_and_ts(sql)
        sql = self.shorter(sql)
        return sql

    def prettify_sql(self, sql):
        if len(sql) > 400:
            return sql[0:200] + '...' + sql[-200:]
        return sql

    def read_by_chunks(self, fd, size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = fd.read(size)
            if not data:
                break
            yield data

    def calc_stats(self):
        slow_queries = {}
        with open(self.tmp_file) as f:
            for e in SlowQueryLog(f):
               if not e.query_time:
                   continue
               try:
                   query_pattern = self.pattern(self.clean(e.query))
               except:
                   pass
               if query_pattern not in slow_queries:
                   slow_queries[query_pattern] = []
               slow_queries[query_pattern].append(e)
        ret = {}
        for query_pattern, entry_list in slow_queries.items():
            entry = {
                    'org': entry_list[0],
                    'avg_query_time': sum([e.query_time for e in entry_list]) / len(entry_list),
                    'count': len(entry_list),
                    'query_pattern': query_pattern,
                    'query': self.clean(entry_list[0].query),
            }
            ret[query_pattern] = entry
        return ret

    def dump_slow_query_log(self):
        with open(self.log_file) as f:
            with open(self.tmp_file, 'w') as fw:
                status = -1
                for piece in self.read_by_chunks(f):
                    if status == -1:
                        pos = piece.find('# Time: %s' % self.start_time)
                        if pos < 0:
                            continue
                        else:
                            status = 0
                            fw.write(piece[pos:])
                    else:
                        pos = piece.find('# Time: %s' % self.end_time)
                        if pos < 0:
                            fw.write(piece)
                        else:
                            fw.write(piece[:pos])
                            return

    def parser_from_std(self):
        with open(self.tmp_file, 'w') as fw:
            for line in sys.stdin:
                fw.write(line)
        stats = self.calc_stats()
        res = []
        for query_pattern, entry in stats.items():
                res.append(entry)
        if self.sort == 't':
            res = sorted(res, reverse=True, key=lambda x: x['avg_query_time'])
        elif self.sort == 'a':
            res = sorted(res, reverse=True, key=lambda x: x['avg_query_time'] * x['count'])
        else:
            res = sorted(res, reverse=True, key=lambda x: x['count'])
        for q in res:
            print 'count: %s, avg_time: %.2fs, query: %s' % (q['count'], q['avg_query_time'],\
                    self.prettify_sql(q['query']))
            print '##################################'

    def parser_from_log(self):
        self.dump_slow_query_log()
        stats = self.calc_stats()
        res = []
        for query_pattern, entry in stats.items():
                res.append(entry)
        if self.sort == 't':
            res = sorted(res, reverse=True, key=lambda x: x['avg_query_time'])
        elif self.sort == 'a':
            res = sorted(res, reverse=True, key=lambda x: x['avg_query_time'] * x['count'])
        else:
            res = sorted(res, reverse=True, key=lambda x: x['count'])
        for q in res:
            print 'count: %s, avg_time: %.2fs, query: %s' % (q['count'], q['avg_query_time'],\
                    self.prettify_sql(q['query']))
            print '##################################'

    def start_parser(self):
        if self.log_file:
            self.parser_from_log()
        else:
            self.parser_from_std()

def main():
    parser = argparse.ArgumentParser(description="mysql slow query parser")
    parser.add_argument("-f", "--log-file", type=str, nargs="?", help="the mysql slow query file", default=None)
    parser.add_argument("-b", "--begin-time", type=str, nargs="?", help="the begin time to parse", default=None)
    parser.add_argument("-e", "--end-time", type=str, nargs="?", help="the end time to parse", default=None)
    parser.add_argument("-t", "--tmp-file", type=str, nargs="?", help="the tmp file", default='/tmp/mysql-slow-query-parse')
    parser.add_argument("-s", "--sort", type=str, help="sort method, c: count; t:average time; a:c*t", default='c')
    args = parser.parse_args()
    print 'begin_time: %s, end_time: %s, log_file: %s, sort method: %s' % (args.begin_time,\
            args.end_time, args.log_file, args.sort)
    query_parser = SlowQueryParser(args.begin_time, args.end_time, args.log_file, args.tmp_file, args.sort)
    query_parser.start_parser()

if __name__ == '__main__':
    main()