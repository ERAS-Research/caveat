# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotb.queue import Queue
import math

from caveat.simulation import PhysicalSimulation


class DelayLine(PhysicalSimulation):
    """Delay data by specified number of samples
    """
    def __init__(self, queue_in: Queue|None=None, queue_out: Queue|None=None,
            delay: int=0):
        if queue_in:
            self.queue_in = queue_in
        else:
            self.queue_in = Queue()

        if queue_out:
            self.queue_out = queue_out
        else:
            self.queue_out = Queue()

        self.delay = delay
        self.delay_line = self.delay * [math.nan]

        cocotb.start_soon(self.run())

    async def run(self):
        while True:
            input_value = await self.queue_in.get()
            self.delay_line.append(input_value)
            await self.queue_out.put(self.delay_line[0])
            self.delay_line = self.delay_line[1:]
