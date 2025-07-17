# caveat-blended forastero test environment
# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel
#
# Definition of classes adopted forastero documentation and application examples #FIXME: review whether this applies to this file
# Licensed under the Apache License, Version 2.0
# Copyright 2023, Peter Birch, mailto:peter@lightlogic.co.uk

#FIXME: remove project-specific assumptions/code: ethernet / in-/out-stream naming

import cocotb
from cocotb.handle import HierarchyObject
from forastero.bench import BaseBench
from forastero.io import IORole
from forastero.monitor import MonitorEvent

from caveat.forasteroext.stream import StreamBackpressure, StreamMonitor, \
    StreamInitiator, StreamIO, StreamResponder, StreamTransaction, \
    StreamTransactionLast
from caveat.report import make_report


class Testbench(BaseBench):
    """Augmented testbench environment for ease of interfacing with DUT as well
    as capturing signals and reporting.
    This class is an alternative to 'CaveatBench'.
    """
    def __init__(self, dut: HierarchyObject, config: dict={}) -> None:
        super().__init__(
            dut,
            clk=dut.clk,
            rst=dut.rst,
            clk_drive=True,
            clk_period=8,
            clk_units="ns",
        )
        self._config = config
        self.handle_dict = {}
        self.handle_dict["eth_out_mon"] = []

        self.eth_instream = StreamIO(dut, "rx_fifo_agent_payload_axis",
            IORole.RESPONDER, io_style=io_prefix_style)
        self.eth_outstream = StreamIO(dut,"tx_fifo_agent_payload_axis",
            IORole.INITIATOR, io_style=io_prefix_style)
        # Register drivers and monitors for the stream interfaces
        self.register("eth_in",
            StreamInitiator(self, self.eth_instream, self.clk, self.rst))
        self.register("eth_out",
            StreamResponder(self, self.eth_outstream, self.clk, self.rst, blocking=False))
        self.register("eth_out_mon",
            StreamMonitor(self, self.eth_outstream, self.clk, self.rst))
        self.eth_out_mon.subscribe(MonitorEvent.CAPTURE, self.stream_capture)
        # disable backpressure for downstream data
        self.eth_out.enqueue(StreamBackpressure(ready=True))

    async def stream_capture(self, monitor: StreamMonitor, event: MonitorEvent,
            obj: StreamTransaction):
        """Process data that was captured by monitor
        """
        self.handle_dict[monitor.name].append((obj.timestamp, obj.data))

    async def send(self, data):
        """Pass data to interface
        """
        for datum in data[:-1]:
            self.eth_in.enqueue(StreamTransaction(data=datum))
        self.eth_in.enqueue(StreamTransactionLast(data=data[-1]))

    def reference_stream_append(self, monitor_name, data):
        """Append data/transactions to specified reference stream (scoreboard)
        """
        for item in data:
           obj = StreamTransaction()
           obj.data = item
           self.scoreboard.channels[monitor_name].push_reference(obj)

    def get_config(self, key: str):
        """Read configuration value
        """
        return self._config.get(key, None)

    def append_config(self, config: dict):
        """Append entries to testbench configuration
        """
        self._config = self._config | config

    def clear_config(self) -> None:
        """Clear all entries from testbench configuration
        """
        self._config = dict()

    def generate_plot(self, testname: str=''):
        """Generate visual report of signals
        """
        #collect data for plotting
        #..set testname
        if testname == '':
            testname = "{:s}/{:s}".format(
                            str(self.dut),
                            cocotb.regression_manager._test.name)
        #..assemble config
        cfg_plot = {}
        cfg_plot['data_dict'] = self.handle_dict
        cfg_plot['axis_dict'] = None

        cr.make_report(testname, cfg_plot=cfg_plot)


def io_prefix_style(bus: str|None, component: str,
        role_bus: IORole, role_comp: IORole) -> str:
    mapping = {
        (IORole.INITIATOR, IORole.INITIATOR): "m",
        (IORole.INITIATOR, IORole.RESPONDER): "m",
        (IORole.RESPONDER, IORole.INITIATOR): "s",
        (IORole.RESPONDER, IORole.RESPONDER): "s",
    }
    full_name = f"{mapping[role_bus, role_comp]}"
    if bus is not None:
        full_name += f"_{bus}"
    return f"{full_name}_t{component}"
