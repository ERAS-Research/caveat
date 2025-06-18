#!/usr/bin/env python3

# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Modified Version of Torsten Rueschel's run test file which applies cocotbext functions
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

from afe import AnalogFrontend


@cocotb.test()
async def test_dac_adc(dut):
    #initialization
    dt=1e-9
    frequency=10e6

    # generate a clock
    cocotb.start_soon(Clock(dut.i_clk, 100, units="ns").start())

    #create AXIS interfaces
    #..always ready to read from ADC AXIS
    #dut.m_adc_tready.value = 1


 


    # source = AxiStreamSource(AxiStreamBus.from_prefix(dut, "m_adc"), dut.clk, dut.rst) 
    # sink = AxiStreamSink(AxiStreamBus.from_prefix(dut, "s_adc"), dut.clk, dut.rst)
    ##dut.rst not included but also unneccesary
    source = AxiStreamSource(AxiStreamBus.from_prefix(dut, "m_adc"), dut.clk) 
    sink = AxiStreamSink(AxiStreamBus.from_prefix(dut, "s_adc"), dut.clk)
   
    
    
    #register DUT inputs for monitoring (to plot, etc...)


    #instantiate analog frontend
    afe_in_queue = Queue()
    afe_out_queue = Queue()
    afe = AnalogFrontend(
        in_queue=afe_in_queue, out_queue=afe_out_queue
    )

    xx = []
    yy = []
    zz = []

    Nsample = 700
    for ii in range(Nsample):
        await RisingEdge(dut.i_clk)

        #send sample via AXIS to DAC
        if ((ii//10 > 6) and (ii//10 < 28)) \
        or (ii > 800):
            dut.s_dac_tvalid.value = 0
            xx.append( np.nan )
        else:
            outval = int((.5 + .5*np.sin(2.*np.pi * frequency * dt * ii))  * 2**15)
            await source.send(outval)
            #dut.s_dac_tdata.value = outval
            #dut.s_dac_tvalid.value = 1
            await source.wait()
            xx.append( outval )
        #forward digital output from frontend_digital to analog frontend's DAC
        afe_in_queue.put_nowait(dut.o_dac_data.value)

        #read the analog frontend's ADC and inject into frontend_digital's ADC pin
        try:
            afe_out = afe_out_queue.get_nowait()
            dut.i_adc_data.value = afe_out
            dut.i_adc_valid.value = 1
            yy.append( afe_out )
        except cocotb.queue.QueueEmpty:
            dut.i_adc_valid.value = 0

        zz.append( int( sink.recv()) )


    #plot history of DAC samples and ADC readings
    plt.figure(figsize=(7,4))
    plt.plot(xx, label='DAC')
    plt.plot(yy, label='ADC (from frontend simulation)')
    plt.plot(zz, dashes=(5,3), label='ADC (via AXI)')
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()



if __name__ == "__main__":
    #start simulation
    run(verilog_sources = [
            './rtl/frontend_digital.v',
        ],
        includes = [
            './rtl',
        ],
        defines = [],
        toplevel = "frontend_digital",
        # python_search = ['.'],
        module = "run_test_dac_adc",
        sim_build = "sim_build/",
        timescale = "1ns/1ps",
        force_compile = True,     #force recompile
        parameters = {},
        extra_env = {
            'COCOTB_ANSI_OUTPUT':'1', #colorful output to terminal
            # 'COCOTB_LOG_LEVEL':'WARNING', #set to 'INFO' for more output
            },
        seed = int(0),            #specify seed for python 'random' module
    )

