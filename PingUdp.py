from __future__ import print_function

import socket
import struct
import time


class PingUdp:
    def __init__(self):
        pass

    def ping(self, host, count_tries, max_hops, traceroute):
        destination_address = socket.gethostbyname(host)
        port = 55285

        ttl = 1
        while True:
            # create sockets for sending and receiving data
            receive_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            # set ttl to send packet
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

            # set timeout for receive socket
            receive_timeout = struct.pack("ll", 1, 0)
            receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, receive_timeout)

            # send udp packet to next hop
            if traceroute:
                print(ttl, end=" ")
            send_time = time.time()
            send_socket.sendto(bytes("Hello server!", "utf-8"), (host, port))

            # bind receive socket to send socket port (for ICMP it is curiously)
            receive_socket.bind(("", send_socket.getsockname()[1]))

            finished = False
            current_address = None
            current_name = None
            tries = count_tries
            while not finished and tries > 0:
                try:
                    # receive data from server/router
                    receive_data, receive_address = receive_socket.recvfrom(512)
                    receive_time = time.time()
                    finished = True
                    current_address = receive_address[0]

                    try:
                        # data come, check to sender address to Domain name (DNS)
                        current_name = socket.gethostbyaddr(current_address)[0]
                    except socket.error:
                        # if not domain
                        current_name = current_address
                except socket.error:
                    # if timeout come in
                    tries -= 1
                    if traceroute:
                        print("*", end=" ")

            send_socket.close()
            receive_socket.close()

            if current_address is not None:
                current_host = "{0} ({1})".format(current_name, current_address)
            else:
                current_host = ""
            if traceroute:
                print(current_host)

            if current_address == destination_address:
                print("Ping to {0}({1} successful ttl={2} RTT: {3} ms)".format(destination_address, host, ttl,
                                                                               receive_time - send_time * 1000))
                break

            ttl += 1
            if ttl > max_hops:
                if not traceroute:
                    print("Server {0}({1}) not found, try to use ICMP ping".format(destination_address, host))
                break
