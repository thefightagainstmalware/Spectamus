import ipaddress
from typing import Union

DISALLOWED_IP4_RANGES = [
    ipaddress.IPv4Network("0.0.0.0/8"),
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("100.64.0.0/10"),
    ipaddress.IPv4Network("127.0.0.0/8"),
    ipaddress.IPv4Network("169.254.0.0/16"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.0.0.0/24"),
    ipaddress.IPv4Network("192.0.2.0/24"),
    ipaddress.IPv4Network("192.88.99.0/24"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("198.18.0.0/15"),
    ipaddress.IPv4Network("198.51.100.0/24"),
    ipaddress.IPv4Network("203.0.113.0/24"),
    ipaddress.IPv4Network("224.0.0.0/4"),
    ipaddress.IPv4Network("233.252.0.0/24"),
    ipaddress.IPv4Network("240.0.0.0/4"),
    ipaddress.IPv4Network("255.255.255.255/32"),
]

DISALLOWED_IP6_RANGES = [
    ipaddress.IPv6Network("::/128"),
    ipaddress.IPv6Network("::1/128"),
    ipaddress.IPv6Network("fe80::/10"),
    ipaddress.IPv6Network("fc00::/7"),
    ipaddress.IPv6Network(
        "::ffff:0:0/96"
    ),  # if we cannot check the ipv6 mapped network, don't use it
    ipaddress.IPv6Network("::ffff:0:0:0/96"),
    ipaddress.IPv6Network("64:ff9b::/96"),
    ipaddress.IPv6Network("2002::/16"),
    ipaddress.IPv6Network("2001::/32"),
    ipaddress.IPv6Network("2001:2::/48"),
    ipaddress.IPv6Network("2001:20::/28"),
    ipaddress.IPv6Network("2001:db8::/32"),
    ipaddress.IPv6Network("100::/64"),
    ipaddress.IPv6Network("ff00::/8")
]


def in_disallowed_range(
    addr: ipaddress.IPv4Address,
    ranges: "list[Union[ipaddress.IPv6Network, ipaddress.IPv4Network]]",
):
    for range in ranges:
        if addr in range:
            return False  # not safe
    return True  # safe


def check_ip(ip: str):
    """Determines if an IP address is safe to send a request to, i.e. not on a private network

    Args:
        ip (str): the ip address
    """
    addr = ipaddress.ip_address(ip)
    if addr.version == 6:
        if addr.ipv4_mapped:
            return in_disallowed_range(addr.ipv4_mapped, DISALLOWED_IP4_RANGES)
        else:
            return in_disallowed_range(addr, DISALLOWED_IP6_RANGES)
    if addr.version == 4:
        return in_disallowed_range(addr, DISALLOWED_IP4_RANGES)
