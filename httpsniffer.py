import argparse
import scapy.all as scapy
from pktprocessor import process_packets


count = 1

def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packets)


parser = argparse.ArgumentParser(description='Packet inspection for Cyber Security Reseach Team')
parser.add_argument('--label-threat', action='store_true', help='Auto-labelling inbound payload as a threat')
parser.add_argument('--label-normal', action='store_true', help='Auto-labelling inbound payload as normal payload')
parser.add_argument('--technique', type=str, help='Specify SQLi attack technique')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--get', action='store_true', help='Capture GET request')
group.add_argument('--post', action='store_true', help='Capture POST request')

args = parser.parse_args()

print("Listening...")
sniff_packet('lo')
