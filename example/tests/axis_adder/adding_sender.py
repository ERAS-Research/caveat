#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Start sanimut cocotb-based emulator with communication interface via socket
"""


import os
import cocotb

import logging
import sys
import threading
import time
import socket
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/'))
if module_path not in sys.path:
    sys.path.append(module_path)
from caveat.caveatbench import CaveatBench
from caveat.augmented_handle import create_interface_socket_to_axis
from caveat import physical




# def communication_operation(caveat_socket):
#     """Main thread to pass packets between interfaces
#     """
#     #set timeout for blocking loop in case of no incoming packets
#     caveat_socket.settimeout(0)
#     stop=False
#     buffer_size = 8192
#     while not stop:
#         #forward packets from socket to AXIS
#         message = None
#         try:
#             message = caveat_socket.recv(buffer_size)
#             print('SOCK>DEV', list(message), flush=True)
#         except:
#             pass

#         #foward packets from AXIS to socket
#         try:
#             message = self.axis_sink.recv_nowait(compact=True)
#             if message:
#                 if self.verbose:
#                     print('DEV>SOCK', list(message), flush=True)
#                 self.socket.sendto(bytearray(message), (self.remote_address, self.remote_port))
#         except cocotb.queue.QueueEmpty:
#             pass






remote_address = "127.0.0.1"
remote_port = 20002
local_port = 20000


caveat_socket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
caveat_socket.bind(('', local_port))
caveat_socket.settimeout(0)
stop=False
buffer_size = 8192








#TODO: register DUT inputs for monitoring (to plot, etc...)

#start emulator
while True:
    messageinput=None
    message=input("numbers to add:")
    message=message.strip().split()
    received=None
    if len(message)==2:
        try:
            message = [int(xx) for xx in message]
            caveat_socket.sendto(bytearray(message), (remote_address, remote_port))
            print("waiting for response...")
            start=time.time()
            while True:
                current=time.time()
                if current-start>5:
                    print("timeout")
                    received=None
                    break
                try:
                    message = caveat_socket.recv(buffer_size)
                    print('SOCK>DEV', list(message), flush=True)
                    break
                except:
                    pass
        except ValueError:
            print("need to print two space separated integers")

    else:
        print("length needs to be exactly two")
        pass


#clean up
#FIXME: never reaching this, if receiving SIGINT or SIGTERM; this should be triggered through an independent process
dut._if_socket_handle.stop = True
dut._if_socket_handle.communication_stop()


