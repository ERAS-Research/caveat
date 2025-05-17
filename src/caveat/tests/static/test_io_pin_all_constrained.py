# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
sanimut static verification
"""


def test_inout_pin_all_constrained(pin_constraints, net_specification):
    """Verify that all physical pins are constrained: starting with a list of
    netlisted pins, verify that
     - corresponding pin constrains exist, and
     - no excess pin constraints exist, as this suggests an incomplete netlist.

    Requires the following fixtures:
      pin_constraints: dict=fileio.xdc_parser.read_xdc(...)
      net_specification: dict=fileio.netlist_parser.read_netspec_from_csv(...)
    """
    list_unchecked = list(net_specification.keys())
    list_checked = list()
    for pin in pin_constraints:
        assert (pin['name'] in list_unchecked + list_checked), "constrained pin '{:s}' unconnected or missing in net specification".format(pin['name'])

        #TODO: add detailed constraint verification here

        #move checked pin from 'list_unchecked' to 'list_checked'
        if pin['name'] in list_unchecked:
            list_unchecked.remove(pin['name'])
            list_checked.append(pin['name'])

    assert list_unchecked == [], "netlist contains unconstrained pins: {:}".format(' '.join(list_unchecked))
