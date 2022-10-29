import certifi

with open("/usr/local/share/ca-certificates/mitmproxy.crt") as mitm:
    with open(certifi.where(), "a") as cert:
        cert.write(mitm.read())
