import time
import requests

def tail(logfile):
    logfile.seek(0, 2)
    while True:
        0
        line = logfile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def send_request(url, payload, method):
    if method == "GET":
        res = requests.get(url, params=payload)
    elif method == "POST":
        res = requests.post(url, data=payload)
    # print(res.status_code)
    
