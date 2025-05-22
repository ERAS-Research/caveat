# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
static verification
"""


import math
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))  #FIXME: refactor module import
from caveat.fileio import xilinx_package_spec


def test_pin_constraint_voltage_banks_coherence(kintex7_iopin_specification,
        net_specification, pin_constraints):
    """Verify that all physical pins are constrained: starting with a list of
    netlisted pins, verify that
     - corresponding pin constrains exist, and
     - no excess pin constraints exist, as this suggests an incomplete netlist.

    Requires the following fixtures:
      kintex7_iopin_specification: fileio.xilinx_package_spec.read_in_package_specification(...)
      net_specification: dict=fileio.netlist_parser.read_netspec_from_csv(...)
      pin_constraints: dict=fileio.xdc_parser.read_xdc(...)
    """
    #verify presence of meaningful input data
    assert kintex7_iopin_specification != None, "Missing Kintex7 vendor I/O pin specification"
    assert net_specification != None, "Missing netlist design specification"
    assert pin_constraints != None, "Missing netlist design specification"

    vbank = dict()
    for pin in pin_constraints:
        iostandard_voltage = xilinx_package_spec.get_pin_voltage_max_from_iostandard(pin['IOSTANDARD'])
        assert not math.isnan(iostandard_voltage), \
            "Unrecognized iostandard: {:s} for pin {:s}".format(
                pin['IOSTANDARD'],
                pin['name'])

        pin_vbank = xilinx_package_spec.get_voltage_bank(
                        kintex7_iopin_specification,
                        pin['name'])

        if net_specification.get(pin['name'], {}).get('inout') in ['output', 'inout']: #FIXME: read inout specification from constraints and top-level module instead
            #record voltage bank configuration, if not yet constrained
            if (pin_vbank not in vbank.keys()):
                vbank[pin_vbank] = iostandard_voltage

            assert vbank[pin_vbank] == iostandard_voltage, \
                "Conflicting voltage configuration for bank {:s}: previously configured as {:.1f}V, but pin {:s} requires {:.1f}V".format(
                    pin_vbank,
                    vbank[pin_vbank],
                    pin['name'],
                    iostandard_voltage)

