
#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel, Murray Ferris

"""
Demonstrator for transfer of samples from digital to analog domain, generic
simulation of physical frontend, and analog to digital transfer.
"""


import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Edge
from cocotb_test.simulator import run



@cocotb.test()
async def axis_adder(dut):
    clock_name = "clk"
    clock = getattr(dut, clock_name)
    period = 10

    cocotb.start_soon(Clock(clock, period, units="ns").start())

    input_a=int(10)
    dut.value_a.value = input_a
    input_b= int(7)
    dut.value_b.value = input_b

    await Edge(dut.result)
    output = int(dut.result.value)


    assert output == (input_a + input_b), "adder did not result in the correct addition:{} + {} =/= {}".format(input_a, input_b, output)

    print("\n \n   Adder Result: {} + {} = {} \n \n ".format(input_a, input_b, output))


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