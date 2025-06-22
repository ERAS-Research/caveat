# caveat-blended forastero test environment
# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel
#
# Definition of classes adopted forastero documentation and application examples
# Licensed under the Apache License, Version 2.0
# Copyright 2023, Peter Birch, mailto:peter@lightlogic.co.uk

from collections.abc import Callable
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.handle import HierarchyObject
from cocotb.queue import Queue
from dataclasses import dataclass
from forastero import BaseTransaction, BaseMonitor, BaseIO
from forastero.driver import BaseDriver
from forastero.io import IORole


@dataclass(kw_only=True)
class StreamTransaction(BaseTransaction):
    data: int = 0

class StreamTransactionLast(StreamTransaction):
    pass

@dataclass(kw_only=True)
class StreamBackpressure(BaseTransaction):
    ready: bool = True
    cycles: int = 1


class StreamMonitor(BaseMonitor):
    def __init__(self, *args, **kwargs):
        super(StreamMonitor, self).__init__(*args, **kwargs)
        self._values = Queue()

    async def monitor(self, capture: Callable) -> None:
        while True:
            await RisingEdge(self.clk)
            if self.rst.value == 1:
                continue
            if self.io.get("valid", 1) and self.io.get("ready", 1):
                capture(StreamTransaction(data=self.io.get("data", 0)))


class StreamInitiator(BaseDriver):
    async def drive(self, obj: StreamTransaction) -> None:
        self.io.set("data", obj.data)
        self.io.set("valid", 1)
        if isinstance(obj, StreamTransactionLast):
            self.io.set("last", 1)
        else:
            self.io.set("last", 0)
        while True:
            await RisingEdge(self.clk)
            if self.io.get("ready", 1):
                break
        self.io.set("valid", 0)
        self.io.set("last", 0)


class StreamResponder(BaseDriver):
    async def drive(self, obj: StreamBackpressure) -> None:
        self.io.set("ready", obj.ready)
        await ClockCycles(self.clk, obj.cycles)


class StreamIO(BaseIO):
    """Configuration for AXI-Stream #FIXME: rename class?
    """
    def __init__(
        self,
        dut: HierarchyObject,
        name: str | None,
        role: IORole,
        io_style: Callable[[str | None, str, IORole, IORole], str] | None = None,
    ) -> None:
        super().__init__(
            dut=dut,
            name=name,
            role=role,
            init_sigs=["data", "valid", "last"],
            resp_sigs=["ready"],
            io_style=io_style,
        )
