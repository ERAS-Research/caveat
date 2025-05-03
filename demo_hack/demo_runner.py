#!/usr/bin/env python3

import pytest
import cocotb
import os
from cocotb_test.simulator import run

def test_runner():
    path_dut = os.environ.get('SANIMUT_FPGA_SOURCEDIR')
    print(path_dut)
    print(os.environ.get('SANIMUTROOT'))
    print('YO', path_dut)
    run(verilog_sources = [
            os.path.join(path_dut, 'trxpc1_core.v'),
            # os.path.join(path_dut, 'def_function_util.vh'),
            # os.path.join(path_dut, 'def_communication_protocol.vh'),
            # os.path.join(path_dut, 'def_trxpc1_static_configuration.vh'),
        ],
        includes = [
            '.',
            path_dut
        ],
        defines = [],
        toplevel = "trxpc1_core",
        python_search = ['.', ],
        module = "cocotb_tb",
        # sim_build = "sim_build/",
        timescale = "1ns/1ns",
        # parameters = parameters,         # use to pass differing constant values
        # extra_env = parameters,          # use to pass extra environment arguments
        force_compile = True,            # force compile regardless of sources not changed
        seed = int,              # specify which seed the python random module will use
    )
