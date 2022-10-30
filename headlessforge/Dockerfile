FROM eclipse-temurin:8
RUN adduser -u 5678 --disabled-password --gecos "" runner && \
apt-get update && \
apt-get install -y --no-install-recommends iproute2 dnsutils curl xvfb python3 python3-pip libxrender1 libxtst6 libxi6 libxcursor1 libxrandr2 x11-xserver-utils
COPY mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
COPY natives-armv7l.tar /home/runner/natives-armv7l.tar
# change the above line to the proper arch
COPY usernames.txt /home/runner/usernames.txt
COPY resources /home/runner/resources

COPY overwritecertifi.py /overwritecertifi.py
COPY main.sh /home/runner/main.sh
COPY main.py /home/runner/main.py
RUN keytool -trustcacerts -noprompt -keystore "$JAVA_HOME/jre/lib/security/cacerts" -storepass changeit -importcert -alias digicertassuredidg2 -file "/usr/local/share/ca-certificates/mitmproxy.crt"
RUN python3 -m pip install requests
RUN python3 /overwritecertifi.py
COPY libdl.py /home/runner/libdl.py
RUN su runner -c "cd /home/runner && python3 libdl.py"
RUN mkdir /home/runner/.minecraft/mods -p


CMD ["bash", "/home/runner/main.sh"]