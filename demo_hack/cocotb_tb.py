# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

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

    # run for 1000 cycles, checking for data on each rising edge
    data_buffer = []
    current_packet = []
    n_sample = 0
    n_sample_max = 5
    for cnt in range(1000):
        await RisingEdge(dut.clk)
        #place up to three data samples on RF-Rx sampling port
        #..first transfer
        # OR
        #..transfer complete, place new sample
        if cnt == 0:
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(100)
        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample < n_sample_max):
            n_sample = n_sample + 1
            dut.s_axis_rfrx_tvalid.value = int(1)
            dut.s_axis_rfrx_tdata.value = int(100 + n_sample)
        elif (dut.s_axis_rfrx_tready.value) and (dut.s_axis_rfrx_tvalid.value) and (n_sample >= n_sample_max):
            dut.s_axis_rfrx_tvalid.value = int(0)

        if (dut.m_axis_sys_tvalid.value):
            current_packet.append(int(dut.m_axis_sys_tdata.value))
            if (dut.m_axis_sys_tlast.value):
                data_buffer.append(current_packet)
                current_packet = []

    for ii, pkg in enumerate(data_buffer):
        print('Pkg#', ii, 'data:', pkg)
