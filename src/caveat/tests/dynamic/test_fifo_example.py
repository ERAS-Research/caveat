# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris, Torsten Reuschel

import cocotb
from cocotb_test.run import run
import os
import pytest
import random
import sys

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
print('module path is ', module_path)

if module_path not in sys.path:
    sys.path.append(module_path)
from caveatbench import CaveatBench



axis_fifo_path = module_path + "caveat/hdl/axis_fifo.v"
@cocotb.test()
async def get_fifo_example(dut):
    await get_fifo_example_logic(dut)

async def get_fifo_example_logic(dut, tb: CaveatBench=None):
    """Sends a message to the AXIS FIFO of the FPGA, requesting the status of
    various health related registers.

    Returns: {64bit time}, {16bit temperature}, {16bit fan threshold},
    {32bit fan speed}, 0000_00{2bit bootstrap status}, {8bit debug register readout}
    """
    if tb is None:
        tb = CaveatBench(dut)

    monitored_signals = [
        "s_axis_tdata",
        "m_axis_tdata" ]
    clock_list = ['clk',1]

    await tb.initialize_clock(*clock_list)
    await tb.add_sender_axis(
            prefix="s_axis",
            label='sender',
            clk='clk')
    await tb.add_receiver_axis(
            prefix="m_axis",
            label='receiver',
            clk='clk')
    for signal in monitored_signals:
        await tb.init_monitor(signal, 'clk')

    message = [random.randint(0,255) for xx in range(100)]
    await tb.send_message('sender', message)
    outvalue = await tb.read_message('receiver')
    tb.generate_plot()
    assert outvalue == message, "message not received as sent, expected: {}, got {}".format(message, outvalue)

def test_fifo_example():
    """pytest wrapper to capture test results from cocotb_test runner
    """

    run(module = __name__,
        verilog_sources = [

            '../../rtl/axis_fifo.v',
        ],
        includes =  [
            '../rtl',
        ],
        defines = [],
        toplevel = "axis_fifo",
        sim_build =  "build/sim_build/",
        timescale  = "1ns/1ns",
        force_compile = True,     #force recompile
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            # 'COCOTB_LOG_LEVEL':'WARNING', #set to 'INFO' for more output
            },
        seed = int(0),            #specify seed for python 'random' module
    )




@pytest.hookimpl(optionalhook=True)
def pytest_reporter_context(context, config):
    """Customize pytest report
    """
    context["title"] = "CAVEAT/sanimut dynamic verification"


if __name__ == '__main__':
    pytest.main([
                '-v', '--tb=native', '-ra',
                '--template=html-dots/index.html', '--report=build/results/report_test_dynamic.html', # html reporting
                '-n=4',
                # '-W error'
                # '-W ignore:outdated'
            ],
            plugins=['test_fifo_example']
        )
