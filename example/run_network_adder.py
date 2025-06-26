#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris, Torsten Reuschel

"""
Start sanimut cocotb-based emulator with communication interface via socket
"""

import os
import cocotb
import sys
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb_test.simulator import run

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/'))
if module_path not in sys.path:
    sys.path.append(module_path)
# from caveat.caveatbench import CaveatBench
from caveat import augmented_handle
from caveat.caveatbench import CaveatBench

def splitter(interface_in):
    if ('z' in str(interface_in)) or ('x' in str(interface_in)):
        return [float('nan')]*2
    else:
        return[int(interface_in)>>8, int(interface_in)&0xff]

@cocotb.test()
async def run_network_adder(dut):
    cocotb.start_soon(Clock(dut.clk, 8, units="ns").start())
    tb_env = CaveatBench(dut)
    await tb_env.init_monitor("s_axis_tdata", "clk", callback=splitter)
    await tb_env.init_monitor("m_axis_tdata", "clk")

    #create and connect socket interface
    dut.create_interface_socket_to_axis(
        remote_address = "127.0.0.1",
        remote_port = 20000,
        local_port = 20002,
        axis_bus_module_input = "s_axis",
        axis_bus_module_output = "m_axis")

    #start emulator
    try:
        while True:
            await RisingEdge(dut.clk)
    finally:
        dut._if_socket_handle.stop = True
        dut._if_socket_handle.communication_stop()
        tb_env.generate_plot()


if __name__ == "__main__":
    run(module = "run_network_adder",
        verilog_sources = ['rtl/axis_adder_toplevel.v'],
        toplevel = "axis_adder_toplevel",
        sim_build = 'build/sim_build/',
        timescale  = "1ns/1ps",
        force_compile = True,     #force recompile,
    )
