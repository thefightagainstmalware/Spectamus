#!/bin/bash

iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080

su -c "/home/mitmproxy/.local/bin/mitmdump --mode transparent --showhost -w /home/mitmproxy/mitmproxyout" mitmproxy