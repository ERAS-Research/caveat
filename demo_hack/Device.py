# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
This module implements building blocks for dynamic, i.e. algorithmic,
verification.
"""

from enum import Enum

class TimeBase(Enum):
    """
    Time step basis
    """
    ns = -9
    us = -6
    ms = -3

class Interface(dict):
    """
    Base class for discrete physical signals and buses.
    """

    def __init__(self, direction: str, bitwidth: int, dt: int,
                 time_base: TimeBase):
        self.direction = direction
        self.bitwidth = bitwidth
        self.dt = dt
        self.time_base = time_base

class SingleWire(Interface):
    """
    """
    def __init__(self, direction: str, dt: int, time_base: TimeBase):
        self.direction = direction
        self.bitwidth = 1
        self.dt = dt
        self.time_base = time_base

class UDP(Interface):
    """
    """
    def __init__(self, direction: str, dt: int, time_base: TimeBase):
        self.direction = direction
        self.bitwidth = 8
        self.dt = dt
        self.time_base = time_base


class Device(object):
    """
    Generic device class for interfacing with static and dynamic verification
    tools
    """

    def __init__(self, device_name: str, input_signals = None,
                 output_signals = None, verbose: bool = False):
        """
        Initialize the device settings before connecting

        @param device_name  The name (id) of the device in string format

        @param device_address  The address of the device in string format

        @param verbose  The logging mode for verbose output, default false
        """
        self.device_name = device_name
        self.verbose = verbose

        for insig in input_signals:
            insig
