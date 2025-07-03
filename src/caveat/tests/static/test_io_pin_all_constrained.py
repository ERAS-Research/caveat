# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
static verification
"""


def test_inout_pin_all_constrained(pin_constraints, net_specification):
    """Verify that all physical pins are constrained. Check that
     - corresponding pin constrains exist, and
     - no excess pin constraints exist, as this suggests an incomplete netlist.

    Requires the following fixtures:
      pin_constraints: dict=fileio.xdc_parser.read_xdc(...)
      net_specification: dict=fileio.netlist_parser.read_netspec_from_csv(...)
    """
    pins_constrained = set([pin['name'] for pin in pin_constraints])
    pins_netlisted = set(net_specification.keys())

    excess_constrained = pins_constrained - pins_netlisted
    assert excess_constrained == set([]), \
        "constrained pin(s) unconnected or missing in netlist: {:}".format(
            ' '.join(excess_constrained))

    excess_netlisted = pins_netlisted - pins_constrained
    assert excess_netlisted == set([]), \
        "netlist contains unconstrained pins: {:}".format(
            ' '.join(excess_netlisted))
