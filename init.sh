sudo apt install iptables python3-dev libpcap-dev libnetfilter-queue-dev build-essential
python3 -r requirements.txt
cd python-netfilterqueue
python3 setup.py install
iptables -t nat -A PREROUTING -p tcp --dport 80 -j NFQUEUE --queue-num 1
