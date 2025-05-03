# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

# Simple tests for an counter module
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


def sanimut_rfstream_sample(channel, sample, bitwidth_channel=8, bitwidth_sample=16):
    """Build sanimut channel sample [source_channel, 16bit_I, 16bit_Q]
    """
    pass

@cocotb.test()
async def trxpc1_core_interface(dut):
    # generate a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())


    #indicate ready to receive outputs to core AXIS
    dut.m_axis_sys_tready.value = int(1)

    # run for 50ns checking count on each rising edge
    for cnt in range(5):
        await RisingEdge(dut.clk)
        #place data on RF-Rx sampling port
        dut.s_axis_rfrx_tvalid.value = int(1)
        print(int(1564815 + cnt*100).to_bytes(5, 'big'))
        dut.s_axis_rfrx_tdata.value = int(1564815)# + cnt*100).to_bytes(5, 'big')

        axis_out = zip(dut.m_axis_sys_tdata.value, dut.m_axis_sys_tvalid.value, dut.m_axis_sys_tlast.value)

        print(cnt, axis_out)
