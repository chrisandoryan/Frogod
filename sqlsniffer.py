import scapy.all as scapy
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

MYSQL_PORT = 3306

class MysqlParser(object):
        
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
            struct.pack('256s', ifname[:15].encode())
        )[20:24])

    def bin2ip(self, binary):
        return ".".join([str(x) for x in binary])

    def print_query(self, ts, src, dst, sport, dport, data):
        data = bytes(data)
        if len(data) < 6: return
        cmd = data[4]
        if cmd == COM_QUERY:
            query = "%s %s:%d %s" % (datetime.fromtimestamp(
                ts), src, sport, data[5:].decode().replace("\n", " "))
            print(query)

def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packets,
                filter='dst host 127.0.0.1 and (tcp dst port 3306 or tcp src port 3306)')

def process_packets(packet):
    ip_pkt = packet['IP']
    tcp_pkt = packet['TCP']
    if tcp_pkt.flags & dpkt.tcp.TH_PUSH:
        print("{} => {}".format(packet['TCP'].sport, packet['TCP'].dport))
        if len(tcp_pkt.payload) < 6:
            return
        p.print_query(tcp_pkt.time, p.bin2ip(ip_pkt.src), p.bin2ip(ip_pkt.dst), \
            tcp_pkt.sport, tcp_pkt.dport, tcp_pkt.payload)
        calc_query_exectime(packet['TCP'].sport, packet['TCP'].dport)        

pending_queries = {}

def calc_query_exectime(s, d):
    pending_queries[s] = datetime.now()
    if d in pending_queries:
        print("Query Selesai")
        elapsed = datetime.now() - pending_queries[d]
        return elapsed.total_seconds()
    return

if __name__ == "__main__":
    print("Listening...")

    p = MysqlParser()
    sniff_packet('lo')

"""
TODO:
1. calculate query execution time DONE
2. calculate how many rows returned (on SELECT query)
3. calculate how many rows affected (on INSERT, UPDATE, DELETE query)
"""