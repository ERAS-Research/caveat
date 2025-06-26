# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel, Murray Ferris

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.utils import get_sim_time
from cocotb.triggers import Edge
from cocotb_bus.monitors import Monitor


class CaveatMonitor(Monitor):
    """CaveatMonitor inherits from cocotb_bus and defines _capture() to
    process monitored signals. Used for dedicated capturing.
    """
    def __init__(self, signal: SimHandleBase, little_endian=False):
        self._values = Queue()
        self._signal = signal
        self._coroutine = None
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
                print("val before", val, "type:", type(val))
                print("self little endian:" , self.little_endian)
                if self.little_endian == True:
                    data[1]=int.from_bytes(int(val).to_bytes(int(len(val)/8), byteorder='big'), byteorder='little')
                    print("val after:", data[1])
                self._values.put_nowait(data)
            except ValueError:
                self._values.put_nowait(self._capture(str(self._signal.value)))

    def _capture(self, value):
        """Callback to record changes in a given signal. The function appends
        the most recent  value of the signal up until the current time step, and
        then appends the new value.
        """
        current_time = int(get_sim_time(units='ns'))
        return (current_time, value)
