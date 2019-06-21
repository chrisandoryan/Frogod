import utils
import os
import argparse
import json
import csv
import re
import urllib.parse

def manual_labelling():
    logfile = open("./samples/GET.txt", "r")

    if(args.live):
        for x in utils.tail(logfile):
            if x != '':
                data = json.loads(x)
                print(data['raw_payload'])
                res = input("Classified as [0: normal / 1: threat] ")
    else:
        for l in logfile:
            data = json.loads(l)
            print(data['raw_payload'])
            res = input("Classified as [0: normal / 1: threat] ")
            for num, line in enumerate(logfile, 1):
                if data['raw_payload'] in line:
                    print(line)

def replay_csic_dataset(mode):
    print("Replaying %s packets from CSIC2010\n" % mode)
    print("Format: ")
    # index method url protocol userAgent pragma cacheControl accept acceptEncoding acceptCharset acceptLanguage host connection contentLength contentType cookie payload label
    dataset = open("../output_http_csic_2010_weka_with_duplications_RAW-RFC2616_escd_v02_full.csv", "r")
    csv_reader = csv.reader(dataset, delimiter=',')

    line_count = 0
    send_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(' '.join(row))
            line_count += 1
        else:
            if row[17].strip() == mode:
                raw_payload = urllib.parse.unquote_plus(row[16].strip())
                payload = dict(re.findall(r'(\S+)=(".*?"|\S+)', str(raw_payload)))
                print(payload)
                # print(urllib.parse.urlencode(payload, quote_via=urllib.parse.quote))
                utils.send_request('http://localhost/', payload, row[1])
                send_count += 1
            line_count += 1

    print("Finished sending %d requests" % send_count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data labeler for Cyber Security Reseach Team')
    parser.add_argument('--live', action='store_true', help='Capture GET request')

    args = parser.parse_args()

    replay_csic_dataset("norm")
    
    print("Program finished")
            