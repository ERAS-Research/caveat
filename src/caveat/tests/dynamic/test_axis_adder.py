#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel, Murray Ferris

"""
Demonstrator for transfer of samples from digital to analog domain, generic
simulation of physical frontend, and analog to digital transfer.
"""

import matplotlib.pyplot as plt
import numpy as np
import os

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge
from cocotb_test.simulator import run
from cocotbext.axi import (AxiStreamBus, AxiStreamSource, AxiStreamSink)

from framework.src.caveat.physical import Adder, Attenuator, DelayLine, Loopback
from caveatext.caveatenvironment import CaveatEnvironment







@cocotb.test()
async def axis_adder(dut):
    clock_handle="clk"
    clock=getattr(dut, clock_handle)
    period=10
    cocotb.start_soon(Clock(clock, period, units="ns").start())


if __name__ == '__main__':
    run("verilog_sources" : [
,
            ],
            "includes" : [
                ,
                './rtl',
                '../../../../ip_repo/verilog-ethernet/lib/axis/rtl/',
            ],
            "defines" : [],
            "toplevel" : "fpga_core",
            "sim_build" : "sim_build/",
            "timescale" : "10ns/10ns",
            "force_compile" : True,     #force recompile

            "extra_env" :{
                'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
                # 'COCOTB_LOG_LEVEL':'WARNING', #set to 'INFO' for more output
                },
            "seed" : int(0)           #specify seed for python 'random' module
            )