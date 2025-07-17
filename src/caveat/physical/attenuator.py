# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import cocotb
from cocotb.queue import Queue
import math

from caveat.simulation import PhysicalSimulation


class Attenuator(PhysicalSimulation):
    """Attenuate numerical samples by specified factor
    """
    def __init__(self, queue_in: Queue|None=None, queue_out: Queue|None=None,
            attenuation_factor: float=1.):
        if queue_in:
            self.queue_in = queue_in
        else:
            self.queue_in = Queue()

        if queue_out:
            self.queue_out = queue_out
        else:
            self.queue_out = Queue()

        self.attenuation_factor = attenuation_factor

        cocotb.start_soon(self.run())

    async def run(self):
        while True:
            value = await self.queue_in.get()
            try:
                await self.queue_out.put(self.attenuation_factor * value)
            except:
                await self.queue_out.put(math.nan)
