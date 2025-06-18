
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
    await axis_adder_logic(dut)


async def axis_adder_logic(dut, helper_in=None):
    #initialization
    dt=1e-9
    frequency=10e6

    if helper_in is None:
        tb_env = CaveatEnvironment(dut)
    else:
        helper = helper_in


    ##weve g
    # signal_list=["s_rx_fifo_agent_payload_axis_tdata", "m_tx_fifo_agent_payload_axis_tdata" ]
    clock_list=(['clk',8])
    await tb_env.initialize_clock(*clock_list)
    await tb_env.add_sender(prefix="s_axis", label='sender', clk='clk')
    await tb_env.add_receiver(prefix="m_axis", label='receiver', clk='clk')
    # for signal in signal_list:
    #     await tb_env.start_monitors(signal, "clk")
    await tb_env.send_message('sender', init_message)



    message = tb_env.get_header_from_name("SYS_GET_HWINFO")

    await tb_env.send_message('sender',message)


    Nsample = 1800
    aa=[]
    bb=[]
    cc=[]
    voltage_threshold=5.0
    await helper.wait(250005)
    for ii in range(Nsample):

        await helper.wait(1)
        print("clk is, ", dut.i_clk_adc.value)
        if ii>5:
            if dut.o_data_ouflow.value==1:
                assert dut.o_data_ouflow.value==0, "adc overflow detected!! voltage value of %f detected" %(cc[-4])
        print("ouflow value is, ",dut.o_data_ouflow.value)
        dut.i_conf_rfrx_burst.value=0
        dut.i_conf_rfrx_skip.value=0
        #simulate behaviour of adc that would be hooked up to the verilog file
        if ((ii//10 > 6) and (ii//10 < 28)) \
        or (ii > 800):
            outval = int(0)
        else:
            outval = int((.5 + .5*np.sin(2.*np.pi * frequency * dt * ii))  * 2**15)

        #c_DATAWIDTH defaults to 16
        #now i have a 16 bit reprensentation of a sin wave. is that really what i want currently? no. convert to between 0 and 5.
        aa.append(outval)


        outval_check=5*outval/(2**15)##assume voltage is between 0 and 5 volts
        cc.append(outval_check)

        ouflow_check= True if outval_check>voltage_threshold else False
        await helper.send_message(outval, ouflow=ouflow_check)
        print("message sent: outval", outval, "in volts:", outval_check)


        received_back=await helper.receive_message_nowait()
        print("received back is: ", received_back)
        if received_back !=[]:
            received_back=int.from_bytes(received_back, "little")
            print("value received:", received_back)

            bb.append(received_back)
        print()




    #plot history of DAC samples and ADC readings
    plt.figure(figsize=(7,4))
    plt.plot(aa, label='AXIS input')
    plt.plot(bb, label='after')
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()





def test_adc_ou(config_cocotb_run):
    """pytest wrapper to capture test results from cocotb_test runner as
    configured via fixture 'config_cocotb_run'
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    args=config_cocotb_run.copy()
    args["module"] = (os.path.splitext(os.path.basename(__file__))[0])
    args["toplevel"] = "axis_fifo_modified"     ##how to run tests using a different toplevel than FPGA.V
    args["verilog_sources"] = args["verilog_sources"]+[dir_path+"../../rtl/adder.v",dir_path+"../../rtl/axis_fifo_modified.v"
    ]

    run(**args)
