# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Parse xdc constraint files
"""

import math
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))  #FIXME: refactor module import
from fileio import xilinx_package_spec
from iopin import IOPin, IOPinType


def read_xdc(infilenames: list=[]):
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
                    #extract name of connected port #FIXME: replace by regular expression
                    port_name = line[line.find('get_ports')+9:]
                    if '[' in port_name:
                        port_name = port_name[:port_name.find('[')]
                    if ']' in port_name:
                        port_name = port_name[:port_name.find(']')]
                    port_name = port_name.replace('{','').replace('}','').rstrip().lstrip()
                    propdict['port_name'] = port_name
                    #store extracted information
                    obj.append(
                            IOPin(
                                name = propdict['PACKAGE_PIN'],
                                param = propdict,
                        ))
                #ignore all other definitions
                else:
                    continue
    return obj
