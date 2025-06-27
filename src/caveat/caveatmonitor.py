# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel, Murray Ferris

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.utils import get_sim_time
from cocotb.triggers import Edge, RisingEdge
from cocotb_bus.monitors import Monitor
from cocotbext.axi import AxiStreamMonitor


class CaveatMonitor(Monitor):
    """CaveatMonitor inherits from cocotb_bus and defines _capture() to
    process monitored signals. Used for dedicated capturing.
    """

    def __init__(self, signal: SimHandleBase, callback= lambda x: x, little_endian=False):
        self._values = Queue()
        self._signal = signal
        self._coroutine = None
        self._callback = callback
        self.little_endian=little_endian

    def start(self):
        """Start monitor
        """
        if self._coroutine is not None:
            raise RuntimeError("Monitor already running")
        self._coroutine = cocotb.start_soon(self._run())

    async def _run(self):
        while True:
            await Edge(self._signal)
            try:
                data=self._capture(str(int(self._signal.value)))
                data=list(data)
                val= self._signal.value
                if self.little_endian == True:
                    data[1]=int.from_bytes(int(val).to_bytes(int(len(val)/8), byteorder='big'), byteorder='little')
                self._values.put_nowait(data)
            except ValueError:
                self._values.put_nowait(self._capture(str(self._signal.value)))

    def _capture(self, value):
        """Callback to record changes in a given signal. The function appends
        the most recent  value of the signal up until the current time step, and
        then appends the new value.
        """
        current_time = int(get_sim_time(units='ns'))
        return (current_time, self._callback(value))


class CaveatAxiStreamMonitor(AxiStreamMonitor):
    """overrides some functionality of the basic axistreammonitor to alow
    for a start time to be included in the data frame, as well as avoiding
    actually using the frame as the primary data transmitter.
    Realistically, this could be rewritten to be proprietary
    """
    def __init__(self, bus, clock, callback=None):
        super().__init__(bus, clock)
        self._current_start_time = None
        self.frame_buffer=[]

    async def _run(self):
        tdata = []
        tuser = []
        tlast = []
        tkeep = []
        tid = []
        tdest = []

        while True:
            await RisingEdge(self.clock)
            # detect and capture AXIS transfer
            if self.bus.tvalid.value and self.bus.tready.value:
                if not tdata:
                    self.start_time = get_sim_time('ns')
                tdata.append(int(self.bus.tdata.value))
                tlast.append(int(self.bus.tlast.value) if hasattr(self.bus, 'tlast') else 0)
                tuser.append(int(self.bus.tuser.value) if hasattr(self.bus, 'tuser') else 0)
                tkeep.append(int(self.bus.tkeep.value) if hasattr(self.bus, 'tkeep') else 0)
                tid.append(int(self.bus.tid.value) if hasattr(self.bus, 'tid') else 0)
                tdest.append(int(self.bus.tdest.value) if hasattr(self.bus, 'tdest') else 0)
                # end of frame
                if tlast[-1] == 1:
                    end_time = get_sim_time('ns')
                    data = tdata.copy()
                    clock_period = (end_time - self.start_time) / (len(tdata) - 1)
                    framedata = [data, self.start_time-clock_period, end_time, clock_period]
                    self.frame_buffer.append(framedata)
                    #cleanup
                    tdata.clear()
                    tuser.clear()
                    tlast.clear()
                    tkeep.clear()
                    tid.clear()
                    tdest.clear()
