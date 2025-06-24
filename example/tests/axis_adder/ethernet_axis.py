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
import logging
import sys


from caveatext.ionosphere import IonosphericEcho


module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/'))
if module_path not in sys.path:
    sys.path.append(module_path)
from caveat.caveatbench import CaveatBench
from caveat.augmented_handle import augmented_handle
from caveat import physical

@cocotb.test()
async def interactive_emulator(dut):

        #create testbench
    tb = CaveatBench(dut)
    await tb.initialize_clock('clk', 10)
    await tb.add_sender_axis(prefix='s_axis', label='input', clk='clk')
    await tb.add_receiver_axis(prefix='m_axis', label='output', clk='clk')

    #create and connect socket interface
    dut.create_interface_socket_to_axis(
        remote_address = "127.0.0.1",
        remote_port = 20000,
        local_port = 20002,
        axis_bus_module_input = "s_axis",
        axis_bus_module_output = "m_axis")





    #instantiate analog frontend
    part0 =  physical.DelayLine(delay=100)


    #TODO: register DUT inputs for monitoring (to plot, etc...)

    #start emulator
    while True:
        await RisingEdge(dut.clk)

        #connect RF digital frontend dut with analog frontend
        #..RF digital output >>> analog frontend
        dig_outvalue=tb.read_message_nowait("output")
        if dig_outvalue:
                part0.queue_in.put_nowait(dig_outvalue)

        #..analog frontend >>> RF digital input
        try:
            afe_outvalue = part0.queue_out.get_nowait()
            if afe_outvalue:
               tb.send_message("input",afe_outvalue)
                ##FIXME: dont need this. should instead have a protocol where you can force 2 bytes and send one to input A, one to input B. maybe an Ack back through network? no. only send back result when done adding
        except cocotb.queue.QueueEmpty:
            pass

    #clean up
    #FIXME: never reaching this, if receiving SIGINT or SIGTERM; this should be triggered through an independent process
    dut._if_socket_handle.stop = True
    dut._if_socket_handle.communication_stop()


def test_fifo_throughput():
    """pytest wrapper to capture test results from cocotb_test runner
    """
    run(module = __name__,
        verilog_sources = ['rtl/axis_adder_toplevel.v'],
        toplevel = "axis_adder_toplevel",
        sim_build = 'build/sim_build/',
        timescale  = "10ns/10ns",
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            },
        seed = int(0),
    )
