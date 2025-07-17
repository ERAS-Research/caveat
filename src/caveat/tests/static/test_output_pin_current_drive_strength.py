# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
static verification
"""


import math

from caveat.fileio import xilinx_package_spec


def test_output_pin_current_drive_strength(kintex7_iopin_specification,
        net_specification, pin_constraints):
    """Verify current driving strength with regard to package specification,
    constraints, and netlist specification, i.e. schematic:
        output pin Imax < Vbank/Rload?

    Potential violations are highlighted using warnings, since the maximum
    current refers to driving strength of a pin. This test does not check
    whether a pin is used as output.
    On the other hand, if the netlist specification indicates a large load
    resistance such as Rload=1MOhm for input pins, this test is practically
    guaranteed to pass for all input pin configurations, because of the implied
    current limit.

    Requires the following fixtures:
      kintex7_iopin_specification: fileio.xilinx_package_spec.read_in_package_specification(...)
      net_specification: dict=fileio.netlist_parser.read_netspec_from_csv(...)
      pin_constraints: dict=fileio.xdc_parser.read_xdc(...)
    """
    #verify presence of meaningful input data
    assert kintex7_iopin_specification != None, "Missing Kintex7 vendor I/O pin specification"
    assert net_specification != None, "Missing netlist design specification"
    assert pin_constraints != None, "Missing netlist design specification"

    for pin in pin_constraints:
        pin_iotype = xilinx_package_spec.get_iotype(
                        kintex7_iopin_specification,
                        pin['name'])

        iostandard_voltage = xilinx_package_spec.get_pin_voltage_max_from_iostandard(pin['IOSTANDARD'])
        assert not math.isnan(iostandard_voltage), \
            "Unrecognized iostandard: {:s} for pin {:s}".format(
                pin['IOSTANDARD'],
                pin['name'])

        pin_current = xilinx_package_spec.get_pin_current_max_7series(
                        pin['IOSTANDARD'],
                        pin_iotype)
        assert not math.isnan(pin_current), \
            "Package specification is missing current drive rating for pin {:s}".format(
                pin['name'])

        net_voltage = net_specification.get(pin['name'], {}).get('voltage_max')
        assert not math.isnan(net_voltage), \
            "Netlist specification is missing voltage rating for pin {:s}".format(
                pin['name'])

        net_Rload = net_specification.get(pin['name'], {}).get('Rload')
        assert not math.isnan(net_Rload), \
            "Netlist specification is missing termination resistance for pin {:s}".format(
                pin['name'])

        if net_specification.get(pin['name'], {}).get('inout') in ['output', 'inout']:
            assert iostandard_voltage/net_Rload < pin_current/1e3, \
                "Insufficient driving strength for termination on pin {:s} for chosen I/O standard {:s}".format(
                    pin['name'],
                    pin['IOSTANDARD'])
            assert net_voltage/net_Rload < pin_current/1e3, \
                "Insufficient driving strength for termination on pin {:s} for specified netlist voltage {:.1f}V".format(
                    pin['name'],
                    net_voltage)
