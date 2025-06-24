# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

from abc import ABC, abstractmethod
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
