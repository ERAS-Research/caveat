#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Start sanimut cocotb-based emulator with communication interface via socket
"""

import numpy as np
import os
import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge
from cocotb_test.simulator import run
from cocotbext.axi import (AxiStreamBus, AxiStreamSource, AxiStreamSink)
from cocotb.binary import BinaryValue
import logging
import sys
import socket
logger = logging.getLogger(__name__)




module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/'))
if module_path not in sys.path:
    sys.path.append(module_path)
from caveat.caveatbench import CaveatBench
from caveat.augmented_handle import create_interface_socket_to_axis
from cocotb.triggers import Edge
from caveat import physical

@cocotb.test()
async def ethernet_adder(dut):





    remote_address = "127.0.0.1"
    remote_port = 20000
    local_port = 20002


    caveat_socket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    caveat_socket.bind(('', local_port))
    caveat_socket.settimeout(0)
    stop=False
    buffer_size = 8192

    clock_name = "clk"
    clock = getattr(dut, clock_name)
    period = 10

    cocotb.start_soon(Clock(clock, period, units="ns").start())



    #start emulator

    #start emulator
    while True:
        try:
            message = caveat_socket.recv(buffer_size)
            print('SOCK>DEV', list(message), flush=True)
            message=list(message)
            dut.value_a.value= message[0]
            dut.value_b.value = message[1]
            if not (message[0]==0 and message[1]==0):
                await Edge(dut.result)
            print("output is", dut.result.value)
            output = int(dut.result.value)
            output=[output]
            print("output is", output)
            caveat_socket.sendto(bytearray(output), (remote_address, remote_port))
            if dut.result.value != 0:
                dut.result.value = 0
                await Edge (dut.result)


        except:
            pass
        #     try:
        #         message = [int(xx) for xx in input]
        #         caveat_socket.sendto(bytearray(message), (remote_address, remote_port))
        #         print("waiting for response...")
        #         start=time.time()
        #         while True:
        #             current=time.time()
        #             if current-start>5:
        #                 print("timeout")
        #                 received=None

        #             except:
        #                 pass
        #     except ValueError:
        #         print("need to print two space separated integers")

        # else:
        #     print("length needs to be exactly two")
        #     pass

    #clean up
    #FIXME: never reaching this, if receiving SIGINT or SIGTERM; this should be triggered through an independent process


def test_ethernet_adder():
    """pytest wrapper to capture test results from cocotb_test runner
    """
    run(module = __name__,
        verilog_sources = [ 'rtl/adder.v', ],
        toplevel = "adder",
        sim_build = 'build/sim_build/',
        timescale  = "1ns/1ps",
        force_compile = True,     #force recompile,
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            },
        seed = int(0),
    )
