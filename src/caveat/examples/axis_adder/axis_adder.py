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

from framework.src.caveat import augmented_handle
from framework.src.caveat.physical import PhysicalSimulation
from caveatext.ionosphere import IonosphericEcho
from tools.util import git_revision


@cocotb.test()
async def interactive_emulator(dut):
    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 8, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_125mhz_ext, 8, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_200mhz, 5, units="ns").start())
    cocotb.start_soon(Clock(dut.clk_50mhz, 20, units="ns").start())
    cocotb.start_soon(Clock(dut.i_pps, 1e9, units="ns").start()) #trigger PPS

    #create and connect socket interface
    dut.create_interface_socket_to_axis(
        remote_address = "127.0.0.1",
        remote_port = 20000,
        local_port = 20002,
        axis_bus_module_input = "s_rx_fifo_agent_payload_axis",
        axis_bus_module_output = "m_tx_fifo_agent_payload_axis")




    #instantiate analog frontend
    part0 = IonosphericEcho(
                delay=100,
                echo_length=1100,
                sample_per_pulse=96,
            )

    #TODO: register DUT inputs for monitoring (to plot, etc...)

    #start emulator
    while True:
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk_125mhz_ext)

        #connect RF digital frontend dut with analog frontend
        #..RF digital output >>> analog frontend
        try:
            dig_outvalue = digital_out.read_nowait()
            if dig_outvalue:
                part0.queue_in.put_nowait(dig_outvalue)
        except cocotb.queue.QueueEmpty:
            pass
        #..analog frontend >>> RF digital input
        try:
            afe_outvalue = part0.queue_out.get_nowait()
            if afe_outvalue:
                digital_in_rxa_ddc.send_nowait(afe_outvalue)
                # digital_in_rxb_ddc.send_nowait(afe_outvalue) #FIXME: create separate/different copy of analog signal for branch B
        except cocotb.queue.QueueEmpty:
            pass

    #clean up
    #FIXME: never reaching this, if receiving SIGINT or SIGTERM; this should be triggered through an independent process
    dut._if_socket_handle.stop = True
    dut._if_socket_handle.communication_stop()


if __name__ == "__main__":
    path_sanimut_fpga_source = '../../../rtl/hdl/'

    #attempt to identify revision from git commit
    parameters = git_revision()
    #start simulation
if __name__ == "__main__":
       run(verilog_sources = [
            '../../rtl/adder.v',
        ],
        includes = [],
        defines = [],
        toplevel = "adder",
        module = "ex_adder_makefile",
        sim_build = "sim_build/",
        timescale = "1ns/1ps",
        force_compile = True,     #force recompile,
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            },
        seed = int(0),            #specify seed for python 'random' module
    )