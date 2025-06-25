#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris

"""
Adder which takes in values from a netowork socket and sends back the resulting sum
"""



import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Edge
from cocotb_test.simulator import run
import socket




@cocotb.test()
async def ethernet_adder(dut):

    remote_address = "127.0.0.1"
    remote_port = 20000
    local_port = 20002
    caveat_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    caveat_socket.bind(('', local_port))
    caveat_socket.settimeout(0)
    buffer_size = 8192
    clock_name = "clk"
    clock = getattr(dut, clock_name)
    period = 10
    cocotb.start_soon(Clock(clock, period, units="ns").start())



    while True:
        try:
            message = caveat_socket.recv(buffer_size)
            print("Received from socket: ", list(message), flush=True)
            message=list(message)
            if message == [100, 100]:
                caveat_socket.close()
                break
            dut.value_a.value = message[0]
            dut.value_b.value = message[1]
            if not (message[0] == 0 and message[1] == 0):
                await Edge(dut.result)
            output = int(dut.result.value)
            output=[output]
            caveat_socket.sendto(bytearray(output), (remote_address, remote_port))
            if dut.result.value != 0:
                dut.result.value = 0
                await Edge (dut.result)
        except:
            pass

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
