FROM python:3.9-slim

RUN adduser -u 5678 --disabled-password --gecos "" mitmproxy && \
apt-get update && \
apt-get install -y --no-install-recommends \
  build-essential \
  ca-certificates \
  curl \
  iptables 
  
COPY pip.conf /etc/pip.conf
# hackish way of ensuring that the piwheels pip.conf gets removed if we aren't on a pi
RUN uname -a | grep -v armv7l && rm /etc/pip.conf || echo "pi"

USER mitmproxy
COPY .mitmproxy /home/mitmproxy/.mitmproxy
# CMD ["bash"]
RUN bash -c "python3 -m pip install --upgrade pip && \
python3 -m pip install pipx && \
python3 -m pipx install mitmproxy"
USER root

COPY main.sh /main.sh

CMD ["/bin/bash", "/main.sh"]