# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotbext.axi import (AxiStreamBus, AxiStreamSource, AxiStreamSink, AxiStreamMonitor)

from .interface import SocketInterface

"""
Augments cocotb simulation handle for use in CAVEAT environment
"""

def create_interface_socket_to_axis(self: cocotb.handle.SimHandleBase,
        remote_address: str, remote_port: int, local_port: int,
        axis_bus_module_input: str = "s_axis",
        axis_bus_module_output: str = "m_axis"):
    self._if_socket = SocketInterface(remote_address=remote_address,
        remote_port=remote_port, local_port=local_port)

    axis_source = AxiStreamSource(AxiStreamBus.from_prefix(self, axis_bus_module_input), self.clk, self.rst)
    axis_sink = AxiStreamSink(AxiStreamBus.from_prefix(self, axis_bus_module_output), self.clk, self.rst)
cocotb.handle.SimHandleBase.create_interface_socket_to_axis = create_interface_socket_to_axis
