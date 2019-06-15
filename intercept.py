import scapy.all as scapy
from scapy_http import http
import argparse
import json
import engine

count = 1


def sniff_packet(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packets)


def process_packets(packet):
    global count
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
        inbound = url if args.get else load
        for s in engine.tokenize(inbound):
            print("Writing inbound payload [{}]".format(count))
            s['request_method'] = request_method.decode("utf-8")
            s['user_agent'] = user_agent.decode("utf-8")
            with open('samples/{}.txt'.format('GET' if args.get else 'POST'), 'a') as f:
                f.write(json.dumps(s) + "\n")
            count += 1


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

parser = argparse.ArgumentParser(description='Packet interceptor for Cyber Security Reseach Team')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--get', action='store_true', help='Capture GET request')
group.add_argument('--post', action='store_true', help='Capture POST request')

args = parser.parse_args()

print("Listening...")
sniff_packet('lo')
