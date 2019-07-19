rm -rf data_temp/*
echo "Cleaning sample directory.."
rm -rf /root/.sqlmap/output/*
echo "Cleaning MySQL log directory.."
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
    sqlmap -u "http://localhost/DVWA/vulnerabilities/sqli/?id=11&Submit=Submit#" --dbms mysql --cookie="security=low; PHPSESSID=gbpftodlp6arohv9b465ncqhac" --technique "${flag[$i]}" --answers="follow=Y" --batch --mobile &
    sqlmap_pid=($!)
    echo "sid=${sqlmap_pid}"
    wait $sqlmap_pid
    kill $listener_pid
    echo "Holding..."
    sleep 3
done
kill slog_pid
# ps -aux | grep python
# pkill -f httpsniffer.py
# todo: use tamper space2comment