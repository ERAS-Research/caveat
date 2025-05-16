# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Parse xdc constraint files
"""

import math

from .iopin import IOPin, IOPinType


def read_xdc(infilenames: list):
    """Read in and parse xdc constraint files based on Vivado user guide UG903
    (v2024.2) December 20, 2024, which defines physical constraints generally by
    means of properties with regard to an object:
        set_property <property> <value> <object list>
    NOTE: This reader is incomplete with regard to the specification and parses
    only a subset of the properties.
    Returns a list of constraint objects
    """
    obj = []
    for infilename in infilenames:
        with open(infilename, 'r') as infile:
            for raw in infile:
                line = raw.lstrip().rstrip()
                #remove comments
                if line.find('#') >= 0:
                    line = line[:line.find('#')]
                #process 'set_property' definitions
                if (line[:12] == 'set_property') and (line.find('-dict') > 0):
                    proplist = line[line.find('-dict {')+7:]
                    proplist = proplist[:proplist.find('}')]
                    proplist = proplist.split()
                    propdict = {}
                    for ii in range(0,len(proplist),2):
                        propdict[proplist[ii]] = proplist[ii+1]
                    obj.append(
                            IOPin(
                                name = propdict['PACKAGE_PIN'],
                                param = propdict,
                        ))
                #ignore all other definitions
                else:
                    continue
    return obj
