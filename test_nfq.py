from scapy.all import *
from netfilterqueue import NetfilterQueue
from pktprocessor import process_packets

nfqueue = NetfilterQueue()
#1 is the iptabels rule queue number, modify is the callback function
nfqueue.bind(1, process_packets) 
try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    pass

