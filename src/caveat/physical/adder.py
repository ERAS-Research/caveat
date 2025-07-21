# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotb.queue import Queue
import numpy as np

from .simulation import PhysicalSimulation


class Adder(PhysicalSimulation):
    """Add two samples from synchronous queues
    """
    def __init__(self, queue_in0: Queue|None=None, queue_in1: Queue|None=None,
            queue_out: Queue|None=None):
        if queue_in0:
            self.queue_in0 = queue_in0
        else:
            self.queue_in0 = Queue()

        if queue_in1:
            self.queue_in1 = queue_in1
        else:
            self.queue_in1 = Queue()

        if queue_out:
            self.queue_out = queue_out
        else:
            self.queue_out = Queue()

        cocotb.start_soon(self.run())

    async def run(self):
        while True:
            value0 = await self.queue_in0.get()
            value1 = await self.queue_in1.get()
            try:
                await self.queue_out.put(value0 + value1)
            except:
                await self.queue_out.put(np.nan)
