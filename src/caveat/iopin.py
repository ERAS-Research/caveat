# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Class for physical input/output pin description
"""

from enum import Enum
import numpy as np


class IOPinType(Enum):
    HIGHZ = 0
    IN = 1
    OUT = 2
    INOUT = 3


class IOPin():
    def __init__(self, name: str, param: dict=dict(),
            iotype: IOPinType=IOPinType.HIGHZ, voltagebank: str=None,
            voltage_max: int=np.nan, current_max: int=np.nan,
            input_impedance: np.complex128=np.nan):
        #store inputs
        self.param = param
        for key, value in locals().items():
            if value is not None:
                self.param[key] = value
