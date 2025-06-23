# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel, Murray Ferris

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.axi import AxiStreamBus, AxiStreamSource, AxiStreamSink
from cocotb.handle import ModifiableObject
import logging

from .caveatmonitor import CaveatMonitor
from .report import make_report


class CaveatBench():
    """Testbench class for embedding DUT in a reproducible test environment
    including extended setup and utility functions related to the DUT (device
    under test).
    This class is an alternative to 'forasteroext.TestBench'.
    """
    def __init__(self, dut, config: dict={}):
        self.dut = dut
        self.monitor_list = {}
        self.handle_dict = {}
        self.sources = {}
        self.sinks = {}
        self._config = config

    def get_clock_handle(self, clk):
        """Obtain handle to clock, which may be identified by string name.
        """
        if isinstance(clk, str):
            return getattr(self.dut, clk)
        elif isinstance(clk, ModifiableObject):
            return clk

    async def initialize_clock(self, clk, period):
        """Start clock in the DUT as identified by name of the clock and
        characterized by a period in nanoseconds (ns)
        """
        cocotb.start_soon(Clock(self.get_clock_handle(clk), period, units="ns").start())

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

    async def add_sender_axis(self, label: str, clk, prefix: str='',
            signals: dict={}, verbosity_level=logging.WARNING):
        """Add AXI-Stream interface capable of sending data to the DUT.
        Takes in either a shared prefix for the prefix_t* wires in the HDL code,
        or a dictionary of signals following the pattern
          {"signal type": "signal_name"} i.e {"tdata": "example_tdata"}
        If both are defined, the prefix is prepended to all signals names.
        """
        clk = self.get_clock_handle(clk)

        if (not signals) and (prefix == ''):
            raise Exception("Neither prefix nor signals defined. Cannot "
                            "instantiate a source.")

        if not signals:
            self.sources[label] = AxiStreamSource(
                AxiStreamBus.from_prefix(self.dut, prefix),
                clk)
            #configure logging
            logging.getLogger('cocotb.{:s}.{:s}'.format(str(self.dut), prefix)).setLevel(verbosity_level)
        else:
            bus = AxiStreamBus(self.dut)
            for key, value in signals.items():
                bus._add_signal(key, prefix + value)
                #configure logging
                logging.getLogger('cocotb.{:s}.{:s}'.format(str(self.dut), prefix + value)).setLevel(verbosity_level)
            self.sources[label] = AxiStreamSource(bus, clk)

    async def add_receiver_axis(self, label: str, clk, prefix: str='',
            signals: dict={}, verbosity_level=logging.WARNING):
        """Add AXI-Stream interface capable of receiving data from the DUT.
        Takes in either a shared prefix for the prefix_t* wires in the HDL code,
        or a dictionary of signals following the pattern
          {"signal type": "signal_name"} i.e {"tdata": "example_tdata"}
        If both are defined, the prefix is prepended to all signals names.
        """
        clk = self.get_clock_handle(clk)

        if (not signals) and (prefix == ''):
            raise Exception("Neither prefix nor signals defined. Cannot "
                            "instantiate a sink.")

        if not signals:
            self.sinks[label] = AxiStreamSink(
                                    AxiStreamBus.from_prefix(self.dut, prefix),
                                    clk)
            #configure logging
            logging.getLogger('cocotb.{:s}.{:s}'.format(str(self.dut), prefix)).setLevel(verbosity_level)
        else:
            bus = AxiStreamBus(self.dut)
            for key, value in signals.items():
                bus._add_signal(key, prefix + value)
                #configure logging
                logging.getLogger('cocotb.{:s}.{:s}'.format(str(bus), prefix + value)).setLevel(verbosity_level)
            self.sinks[label] = AxiStreamSink(bus, clk)

    async def send_message(self, sender_name, message):
        """Send an integer, a list of integers, a byte, or a bytearray to DUT.
        """
        self.sources[sender_name].send_nowait(bytes(message))

    async def read_message(self, receiver_name):
        """Read value out from specified receiver, returning an integer list
        """
        receiver=self.sinks[receiver_name]
        outvalue = await receiver.read()
        return outvalue

    async def wait(self, clk, cycle_num=1):
        """Idle DUT for a specified number of clock cycles.
        """
        clk = self.get_clock_handle(clk)
        for _ in range(cycle_num):
            await RisingEdge(clk)

    def generate_plot(self, truncate=False, testname: str=''):
        """Generate visual report of signals
        """
        #collect data for plotting
        #..set testname
        if testname == '':
            testname = "{:s}/{:s}".format(
                            str(self.dut),
                            cocotb.regression_manager._test.name)
        #..extract plot data from monitors
        for monitor_name, mon in self.monitor_list.items():
            self.handle_dict[monitor_name] = list(mon._values._queue)

        cfg_plot = {}
        cfg_plot['data_dict'] = self.handle_dict
        cfg_plot['axis_dict'] = None
        cfg_plot['truncate'] = truncate

        make_report(testname, cfg_plot=cfg_plot)

    async def init_monitor(self, signal_name, clk):
        """Create and start a monitor for a specific signal
        """
        signal = getattr(self.dut, signal_name)
        self.handle_dict[signal_name] = [signal.value]
        self.monitor_list[signal_name] = CaveatMonitor(signal=signal)
        self.monitor_list[signal_name].start()
