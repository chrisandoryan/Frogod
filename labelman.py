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
                # for key, value in payload:
                #     print(value)
                # print(list(payload.keys()))
                if payload:
                    # field, value = payload.items()[0]
                    print(payload[list(payload.keys())[0]])
                    utils.send_request('http://localhost/DVWA/vulnerabilities/sqli/', {'id': payload[list(payload.keys())[0]], 'Submit': 'Submit'}, row[1])
                    send_count += 1
            line_count += 1
            if send_count >= 3500:
                return

    print("Finished sending %d requests" % send_count)

def map_nominal_to_dataclass(nom):
    return "normal" if nom == 0 else "threat"

impact_indexes = ["N0", "C04", "CIA07", "A"]
def map_nominal_to_impact(nom):
    try:
        return impact_indexes[int(nom)]
    except ValueError:
        return nom

sqltype_indexes = ["nonthreat", "tautology", "incorrect", "union", "piggyback", "storedproc", "inference", "alternate"]
def map_nominal_to_sqltype(nom):
    return sqltype_indexes[int(nom)]

def manual_interactive_labelling():
    line_count = 0
    dataset = open("./samples/GET_labelled.csv", "r")
    raw_data = open("./samples/GET_labelled.csv", "r").readlines()
    csv_reader = csv.reader(dataset, delimiter=',')
    for row in csv_reader:
        # print("Length: " + str(len(row)))
        if len(row) < 8:
            print("Payload: " + row[0])
            attack_type = input("""[0] Nonthreat\n[1] Tautology\n[2] Logically Incorrect Query\n[3] Union Query\n[4] Piggy-backed Query\n[5] Stored Procedures\n[6] Inference\n[7] Alternate Encodings\nInput type [0..7]: """)
            # data_impact = input("Impact [0 (N0) | 1 (C04) | 2 (CIA07) | 3 (A) | bit ]: ")
            # print(map_nominal_to_dataclass(data_class))
            with open("./samples/GET_labelled.csv", "w") as f:
                raw_data[line_count] = raw_data[line_count].strip('\n') + ",{}\n".format(map_nominal_to_sqltype(attack_type))
                # print(raw_data[line_count])
                f.writelines(raw_data)
                line_count += 1
        else:
            print("Already labelled, skipping..")
            line_count += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data labeler for Cyber Security Reseach Team')
    parser.add_argument('--live', action='store_true', help='Capture GET request')
    parser.add_argument('--interactive', action='store_true', help='Capture GET request')

    args = parser.parse_args()

    if args.interactive:
        manual_interactive_labelling()    
    else:
        replay_csic_dataset("norm")
    
    print("Program finished")
            