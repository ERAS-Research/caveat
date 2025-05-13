# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

from abc import ABC, abstractmethod
import math

import cocotb
from cocotb.queue import Queue


class PhysicalSimulation(ABC):
    """Physical simulation block
    """
    @abstractmethod
    def __init__(self, queue_in: Queue|None=None, queue_out: Queue|None=None):
        pass

    @abstractmethod
    async def run(self):
        pass


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
