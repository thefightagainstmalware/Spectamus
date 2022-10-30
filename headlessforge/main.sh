#!/bin/bash
ip route del default
ip route add default via $(dig +short $MITMNAME)

ip route add 1.1.1.1 via 172.19.0.1 # change these 172 ips if the dns doesn't work
ip route add 1.0.0.1 via 172.19.0.1

while [ ! -f /home/runner/toanalyze.jar ]; do
    sleep 0.1 # polling yay
done
mv /home/runner/toanalyze.jar /home/runner/.minecraft/mods/mod.jar
chown runner:runner /home/runner/.minecraft/mods/mod.jar
Xvfb :0 &
chown -R runner /home/runner
su runner -c "export DISPLAY=:0 && cd ~ && python3 /home/runner/main.py"