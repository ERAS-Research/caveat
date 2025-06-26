#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris

"""
Example of using a socket to connect to program on a local network to perform addition
"""

import socket
import time

remote_address = "127.0.0.1"
remote_port = 20002
local_port = 20000

caveat_socket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
caveat_socket.bind(('', local_port))
caveat_socket.settimeout(0)
stop=False
buffer_size = 8192

print("adder over socket demonstration. print two numbers to add in the socket_adder test. send 100 100 to shut down both programs")
#start looping program
while True:
    messageinput = None
    message = input("numbers to add:")
    message = message.strip().split()
    received = None
    if len(message) == 2:
        try:
            message = [int(xx) for xx in message]
            caveat_socket.sendto(bytearray(message), (remote_address, remote_port))
            if message == [100, 100]:
                print("shutdown engaged")
                break
            print("waiting for response...")
            start = time.time()
            while True:
                current = time.time()
                if current - start>5:
                    print("timeout. Numbers may be beyond selected bitwidth (default is (2^4)-1 = 15)")
                    received = None
                    break
                try:
                    message = caveat_socket.recv(buffer_size)
                    print('Received sum:', list(message)[0], flush=True)
                    break
                except:
                    pass
        except ValueError:
            print("need to print two space separated integers")
    else:
        print("length needs to be exactly two")
        pass


