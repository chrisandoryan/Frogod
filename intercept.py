import scapy.all as scapy
from scapy_http import http
import argparse
import json
import engine

def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packets)

def process_packets(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        request_method = get_method(packet)
        load = get_payload(packet)
        cookie = get_cookie(packet)
        user_agent = get_ua(packet)
        content_type = get_content_type(packet)
        referer = get_referer(packet)
        # print url
        # print request_method
        # print load
        # print cookie
        # print user_agent
        # print content_type
        # print referer
        # print(packet.show())
        normalized = engine.tokenize(load)
        print(normalized)

def get_referer(packet):
	return packet[http.HTTPRequest].Referer

def get_method(packet):
	return packet[http.HTTPRequest].Method

def get_cookie(packet):
	return packet[http.HTTPRequest].Cookie

def get_ua(packet):
	return getattr(packet[http.HTTPRequest], 'User-Agent')

def get_content_type(packet):
	return getattr(packet[http.HTTPRequest], 'Content-Type')
        
def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_payload(packet):
    if packet.haslayer(scapy.Raw):
        return packet[scapy.Raw].load
        
sniff_packet('lo')