import scapy.all as scapy
from scapy_http import http

def process_packets(packet):
    global count

    if not os.path.isdir('data_temp'):
        os.mkdir('data_temp')

    if packet.haslayer(http.HTTPRequest):
        ip = get_src_ip(packet)
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
        # print(packet[http.HTTPRequest])
        
        inbound = url if args.get else load
        timestamp = int(time.time())
         
        # print(args.technique)

        # logs = pelotot.parsing(inbound)
        # pelotot.analyze(logs)
        
        for s in engine.tokenize(inbound):
            # print("Writing inbound payload [{}]".format(count))
            print(inbound)
            s['ip'] = ip.decode('utf-8')
            s['request_method'] = request_method.decode("utf-8")
            s['user_agent'] = user_agent.decode("utf-8")
            if (args.label_normal):
                s['label'] = 'normal'
                s['technique'] = 'normal'
            elif (args.label_threat):
                s['label'] = 'threat'
            if (args.technique):
                s['technique'] = args.technique
            # with open('data_temp/{}.json'.format('GET_http' if args.get else 'POST_http'), 'a') as f:
            #     f.write(json.dumps(s) + "\n")
            with open('data_temp/{}.csv'.format('GET_http' if args.get else 'POST_http'), 'a') as f:
                # convert {0: 1.5, 1: 2.2, ...} to [1.5, 2.2, ...] to 1.5 2.2, ...
                s['centrality'] = ' '.join(map(str, list(s['centrality'].values())))
                s['timestamp'] = timestamp
                writer = csv.writer(f)
                # writer.writerow(list(s.keys()))
                writer.writerow(list(s.values()))
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

def get_src_ip(packet):
    if packet.haslayer(scapy.IP):
        return packet[scapy.IP].src
    else:
        return b"UNKNOWN"

def get_payload(packet):
    if packet.haslayer(scapy.Raw):
        return packet[scapy.Raw].load
