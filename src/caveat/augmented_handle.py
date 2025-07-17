# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Augments cocotb simulation handle for use in CAVEAT environment
"""

import cocotb
from cocotbext.axi import AxiStreamBus, AxiStreamSource, AxiStreamSink

from caveat.interface.socket_axis import SocketAXIS


def create_interface_socket_to_axis(self: cocotb.handle.SimHandleBase,
        remote_address: str, remote_port: int, local_port: int,
        axis_bus_module_input: str = "s_axis",
        axis_bus_module_output: str = "m_axis"):
    """Network socket interface for virtual/emulated gateware via AXIS
    """
    #create AXIS interface (with or without reset wire)
    if 'rst' in dir(self):
        axis_sink = AxiStreamSink(
            AxiStreamBus.from_prefix(self, axis_bus_module_output),
            self.clk, self.rst)
        axis_source = AxiStreamSource(
            AxiStreamBus.from_prefix(self, axis_bus_module_input),
            self.clk, self.rst)
    else:
        axis_sink = AxiStreamSink(
            AxiStreamBus.from_prefix(self, axis_bus_module_output),
            self.clk)
        axis_source = AxiStreamSource(
            AxiStreamBus.from_prefix(self, axis_bus_module_input),
            self.clk)
    #create, connect, and open socket
    self._if_socket_handle = SocketAXIS(
        remote_address=remote_address,
        remote_port=remote_port,
        local_port=local_port,
        axis_sink=axis_sink,
        axis_source=axis_source)
cocotb.handle.SimHandleBase.create_interface_socket_to_axis = create_interface_socket_to_axis


def create_interface_serial_to_axis(self: cocotb.handle.SimHandleBase,
        serial_port: str, axis_bus_module_input: str = "s_axis",
        axis_bus_module_output: str = "m_axis"):
    """Serial interface for virtual/emulated gateware via AXIS, e.g. for use
    with I2C, UART, and GPIB.
    """
    pass #FIXME: to be implemented
cocotb.handle.SimHandleBase.create_interface_serial_to_axis = create_interface_serial_to_axis
