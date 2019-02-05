import PingIcmp
from PingUdp import *

host = input("Input host: ")
response = PingIcmp.ping(host, quiet_output=False)


ping_udp = PingUdp()
ping_udp.ping(host, count_tries=3, max_hops=30, traceroute=False)
