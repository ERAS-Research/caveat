# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
sanimut static verification
"""


import math
import os
import sys
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))  #FIXME: refactor module import
from caveat.fileio import xilinx_package_spec


def test_io_voltage_specification_constraint_netlist_match(pin_constraints,
        net_specification):
    """Verify that I/O Standard of pin constraints matches voltage ratings in
    netlist/schematic.

    Requires the following fixtures:
      pin_constraints: dict=fileio.xdc_parser.read_xdc(...)
      net_specification: dict=fileio.netlist_parser.read_netspec_from_csv(...)
    """
    assert net_specification != None
    assert pin_constraints != None

    for pin in pin_constraints:
        iostandard_voltage = xilinx_package_spec.get_pin_voltage_max_from_iostandard(pin['IOSTANDARD'])
        assert not math.isnan(iostandard_voltage), \
            "Unrecognized iostandard: {:s} for pin {:s}".format(
                pin['IOSTANDARD'],
                pin['name'])

        assert pin['name'] in net_specification.keys(), \
            "Pin {:s} not found in netlist specification".format(
                pin['name'])
        net_voltage = net_specification.get(pin['name'], {}).get('voltage_max')
        assert not math.isnan(net_voltage), \
            "Netlist specification is missing voltage rating for pin {:s}".format(
                pin['name'])

        if net_voltage < iostandard_voltage:
            warnings.warn(UserWarning(
                "Netlisted voltage ({:.1f}) may be too low for declared I/O standard '{:s}' on pin {:s}".format(
                    net_voltage,
                    pin['IOSTANDARD'],
                    pin['name'])))
        assert net_voltage <= iostandard_voltage, \
            "Netlisted voltage may exceed declared I/O standard on pin {:s} with iostandard '{:s}' and net specification of {:.1f}V".format(
                pin['name'],
                pin['IOSTANDARD'],
                net_voltage)

