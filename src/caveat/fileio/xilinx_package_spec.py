# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel
#
# package specific information subject to specification and copyright by Xilinx
# as referenced

"""
Import and parse Xilinx package descriptions
"""

import math


def read_in_package_specification(infilename):
    """
    Read in Xilinx package descriptions as provided at
    https://www.xilinx.com/support/package-pinout-files.html
    """
    pinspec = {}
    with open(infilename, 'r') as infile:
        lines = [line.lstrip().rstrip() for line in infile]

    header = ['Pin','PinName','MemoryByteGroup','Bank','VCCAUXGroup','SuperLogicRegion','I/OType','No-Connect']
    #drop descriptors
    lines = lines[3:-2]
    #parse file
    for line in lines:
        entries = line.split()
        pinspec[entries[0]] = dict(zip(header,entries))

    return pinspec

def get_voltage_bank(pinbank_db, iopin: str):
    """
    Import and parse Xilinx package descriptions as provided at
    https://www.xilinx.com/support/package-pinout-files.html
    """
    assert iopin in pinbank_db.keys(), \
        "Unknown pin: {:s}".format(iopin)

    return pinbank_db.get(iopin).get('Bank')

def get_iotype(pinbank_db, iopin: str):
    """
    Import and parse Xilinx package descriptions as provided at
    https://www.xilinx.com/support/package-pinout-files.html
    """
    assert iopin in pinbank_db.keys(), \
        "Unknown pin: {:s}".format(iopin)

    return pinbank_db.get(iopin).get('I/OType')

def get_pin_voltage_max_from_iostandard(iostandard: str):
    """Map I/O standard to nominal peak voltage
    Information according to 7 Series FPGAs SelectIO Resources User Guide
    (UG471), Table 1-55
    """
    iostandard_db = {
        'LVCMOS12': 1.2,
        'LVCMOS15': 1.5,
        'LVCMOS18': 1.8,
        'LVCMOS25': 2.5,
        'LVCMOS33': 3.3,
        'LVDS': 1.8,
        'LVDS_25': 2.5,
        }
    return iostandard_db.get(iostandard, math.nan)

def get_io_voltage_max_from_iotype_7series(iotype: str):
    """Information according to 7 Series FPGAs SelectIO Resources User Guide
    (UG471), Table 1-1
    """
    iotype_db = {
        'HR': 3.3,
        'HP': 1.8,
        }
    return iotype_db.get(iotype, math.nan)

def get_pin_current_max_7series(iostandard: str, iotype: str):
    """Information according to 7 Series FPGAs SelectIO Resources User Guide
    (UG471), Table 1-8
    """
    iostandard_db = {
        'LVDS':     {'HR':24, 'HP':16}, #FIXME: unconfirmed information, cf. ug471
        'LVDS_25':  {'HR':16, 'HP':math.nan}, #FIXME: unconfirmed information, cf. ug471
        'LVCMOS12': {'HR':12, 'HP':8},
        'LVCMOS15': {'HR':16, 'HP':16},
        'LVCMOS18': {'HR':24, 'HP':16},
        'LVCMOS25': {'HR':16, 'HP':math.nan},
        'LVCMOS33': {'HR':16, 'HP':math.nan},
        'LVTTL': {'HR':24, 'HP':math.nan},
        }
    return iostandard_db.get(iostandard).get(iotype)
