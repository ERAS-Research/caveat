#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris

"""
Example of using a socket to interact with network socket, e.g. send integers to
emulator and receive their sum
"""

import socket
import time

remote_address = "127.0.0.1"
remote_port = 20002
local_port = 20000
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(('', local_port))
sock.settimeout(0)

print("User interface for 'adder over network' example. Enter two integers " \
      "and press enter to add. Send 255 255 to shut down.")
while True:
    req = input('Enter two integers to add: ')
    req = req.strip().split()
    if not (len(req) == 2):
        req = [int(req[0]), 0]
    req = [int(rr) for rr in req]
    print('Requesting', ' + '.join([str(rr) for rr in req]))
    sock.sendto(bytearray(req), (remote_address, remote_port))
    if req == [255, 255]:
        print("Shutting down..")
        break

    start = time.time()
    while True:
        if (time.time() - start) > 5:
            print('Timeout... please try again')
            break
        try:
            message = sock.recv(8192)
            print('Received sum:', list(message)[0], flush=True)
            break
        except:
            pass
