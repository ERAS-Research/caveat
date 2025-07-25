#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris, Torsten Reuschel

import cocotb
from cocotb_test.run import run
import random

from caveat.caveatbench import CaveatBench


@cocotb.test()
async def loopback_throughput(dut):
    """Pass a random sequence of bytes through AXIS.
    """
    #create testbench
    tb = CaveatBench(dut)
    #..initialize clock and input/output interfaces
    await tb.initialize_clock('clk', 10)
    await tb.add_sender_axis(prefix='s_axis', label='input', clk='clk')
    await tb.add_receiver_axis(prefix='m_axis', label='output', clk='clk')
    #..set up monitoring
    for signal in ['s_axis_tdata', 'm_axis_tdata']:
        await tb.init_monitor(signal)

    #pass sequence
    input_sequence = [random.randint(0,255) for xx in range(100)]
    await tb.wait('clk', 1)
    await tb.send_message('input', input_sequence)
    received_sequence = await tb.read_message('output')
    assert received_sequence == input_sequence, 'Sequence not received as sent.'

    #export illustration of data transfer
    tb.generate_plot()


def test_loopback_throughput():
    """pytest wrapper to capture test results from cocotb_test runner
    """
    run(module = __name__,
        verilog_sources = ['rtl/axis_loopback.v'],
        toplevel = "axis_loopback",
        sim_build = 'build/sim_build/',
        timescale  = "10ns/1ps",
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            },
        seed = int(0),
    )
