import time
import requests

def tail(logfile):
    logfile.seek(0, 2)
    while True:
        line = logfile.readline()
        if not line:
            time.sleep(0.01)
            continue
        # print(line)
        yield line

def send_request(url, payload, method):
    if method == "GET":
        res = requests.get(url, params=payload)
    elif method == "POST":
        res = requests.post(url, data=payload)
    # print(res.status_code)

def expand(x):
    yield x
    while x.payload:
        x = x.payload
        yield x


    
