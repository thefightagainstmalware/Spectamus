FROM eclipse-temurin:8
RUN adduser -u 5678 --disabled-password --gecos "" runner && \
apt-get update && apt-get install -y --no-install-recommends iproute2 dnsutils curl traceroute iptables

COPY headlessforge.jar /home/runner/headlessforge.jar
COPY mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
COPY main.sh /main.sh

CMD ["bash", "main.sh"]