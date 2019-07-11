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
    sqlmap -u "http://localhost/?email=rob.star@gmail.com" --dbs mysql --level 3 --risk 3 --technique "${flag[$i]}" --answers="follow=Y" --batch --mobile &
    sqlmap_pid=($!)
    echo "sid=${sqlmap_pid}"
    wait $sqlmap_pid
    kill $listener_pid
    echo "Holding..."
    sleep 3
done

# ps -aux | grep python
# pkill -f httpsniffer.py
# todo: use tamper space2comment