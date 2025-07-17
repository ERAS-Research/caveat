# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotb.queue import Queue

from caveat.simulation import PhysicalSimulation


class Loopback(PhysicalSimulation):
    """Loopback device
    """
    def __init__(self, queue_in: Queue|None=None, queue_out: Queue|None=None):
        if queue_in:
            self.queue_in = queue_in
        else:
            self.queue_in = Queue()

        if queue_out:
            self.queue_out = queue_out
        else:
            self.queue_out = Queue()

        cocotb.start_soon(self.run())

    async def run(self):
        while True:
            value = await self.queue_in.get()
            await self.queue_out.put(value)
