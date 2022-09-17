#!/bin/bash
ip route del default
ip route add default via $(dig +short $MITMNAME)
ip route add 1.1.1.1 via 172.19.0.1
ip route add 1.0.0.1 via 172.19.0.1
# dig +trace google.com
keytool -trustcacerts -noprompt -keystore "$JAVA_HOME/jre/lib/security/cacerts" -storepass changeit -importcert -alias digicertassuredidg2 -file "/usr/local/share/ca-certificates/mitmproxy.crt"
while [ ! -f /home/runner/toanalyze.jar ]; do
    sleep 0.1 # polling yay
done

su runner -c "$JAVA_HOME/bin/java -jar /home/runner/headlessforge.jar /home/runner/toanalyze.jar 2>&1"