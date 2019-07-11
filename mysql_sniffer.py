#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Overview
========

A small but useful tool to sniffer mysql query
contact: qingqibai@gmail.com

Usage summary
=============

You need to install python-pypcap and python-dpkt to run this tool
you may:
    apt-get install python-pypcap
    apt-get install python-dpkt
or:
    pip install python-pypcap
    pip install python-dpkt

How to use mysql-sniffer to sniffer query::
    You can get help with ./mysql-sniffer -h or ./mysql-sniffer --help
    ./mysql -ieth1 -p3306 -r0.2
    ./mysql-sniffer -ieth0 -f'host 192.168.20.54 and dst port 3306' -r0.1
    -i or --interface: the interface you want to siniffer
    -p or --port: the mysql port you use
    -f or --filter: filter, defalut None, would use "dst you host and tcp dst port you port 
    -r or --radio: filter radio, from 0 to 1, default 1 means sniffer all query
    -o or --output-file: output file, if set it will print the query to this file instead of stdout, defult None.
"""

import argparse
import pcap
import dpkt
import socket
import fcntl
import struct
from random import random
from datetime import datetime
from functools import wraps

# mysql commands
# http://dev.mysql.com/doc/internals/en/client-server-protocol.html
COM_SLEEP = 0
COM_QUIT = 1
COM_INIT_DB = 2
COM_QUERY = 3
COM_FIELD_LIST = 4
COM_CREATE_DB = 5
COM_DROP_DB = 6
COM_REFRESH = 7
COM_SHUTDOWN = 8
COM_STATISTICS = 9
COM_PROCESS_INFO = 10
COM_CONNECT = 11
COM_PROCESS_KILL = 12
COM_DEBUG = 13
COM_PING = 14
COM_TIME = 15
COM_DELAYED_INSERT = 16
COM_CHANGE_USER = 17
COM_BINLOG_DUMP = 18
COM_TABLE_DUMP = 19
COM_CONNECT_OUT = 20
COM_REGISTER_SLAVE = 21
COM_STMT_PREPARE = 22
COM_STMT_EXECUTE = 23
COM_STMT_SEND_LONG_DATA = 24
COM_STMT_CLOSE = 25
COM_STMT_RESET = 26
COM_SET_OPTION = 27
COM_STMT_FETCH = 28
COM_DAEMON = 29
COM_END = 30

class MysqlSniffer(object):

    def __init__(self, interface, port, filter, ratio, outfile):
        self.interface = interface
        self.port = port
        self.filter = filter
        self.ratio = ratio
        self.output_file = outfile


    def memoize(obj):
        cache = obj.cache = {}
        @wraps(obj)
        def memoizer(*args, **kwargs):
            if args not in cache:
                cache[args] = obj(*args, **kwargs)
            return cache[args]
        return memoizer

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])


    def bin2ip(self, binary):
        return ".".join([str(x) for x in map(ord, binary)])

    def print_query(self, ts, src, dst, sport, dport, data):
        if len(data) < 6:
            return
        cmd = ord(data[4])
        if cmd == COM_QUERY:
            if random() > self.ratio:
                return
            query = "%s %s:%d %s" % (datetime.fromtimestamp(ts), src, sport, data[5:].replace("\n", " "))
            if self.output_file:
                with open(self.output_file, 'a') as f:
                    f.write(query + "\n")
            else:
                print query

    def start_sniffer(self):
        pc = pcap.pcap(name = self.interface)
        if not self.filter:
            self.filter = "dst host %s and tcp dst port %d" % (self.get_ip_address(self.interface), self.port)
        print 'sniffer filter: %s' % self.filter
        pc.setfilter(self.filter)
        decode = { pcap.DLT_LOOP : dpkt.loopback.Loopback,
                   pcap.DLT_NULL : dpkt.loopback.Loopback,
                   pcap.DLT_EN10MB : dpkt.ethernet.Ethernet }[pc.datalink()]
        for ts, raw_pkt in pc:
            ip_pkt = decode(raw_pkt).data
            tcp_pkt = ip_pkt.data
            if tcp_pkt.flags & dpkt.tcp.TH_PUSH:
                if len(tcp_pkt.data) < 6:
                    continue
                self.print_query(ts, self.bin2ip(ip_pkt.src), self.bin2ip(ip_pkt.dst), \
                        tcp_pkt.sport, tcp_pkt.dport, tcp_pkt.data)

def main():
    parser = argparse.ArgumentParser(description="Sniffer mysql.")
    parser.add_argument("-i", "--interface", type=str, nargs="?", help="interface you want to sniffer", default="eth1")
    parser.add_argument("-p", "--port", type=int, nargs="?", help="the mysql port used", default=3306)
    parser.add_argument("-f", "--filter", type=str, nargs="?", help="packet filter", default=None)
    parser.add_argument("-r", "--ratio", type=float, nargs="?", help="filter ratio, from 0 to 1", default=1) # 100%
    parser.add_argument("-o", "--output-file", type=str, nargs="?", help="output file", default=None)
    args = parser.parse_args()
    sniffer = MysqlSniffer(args.interface, args.port, args.filter, args.ratio, args.output_file)
    print 'ratio=%f, o=%s' % (args.ratio, args.output_file)
    sniffer.start_sniffer()
    
if __name__ == "__main__":
    main()