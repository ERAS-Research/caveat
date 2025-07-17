# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Parse verilog code
"""

def read_portmode(infilename: str):
    """Rudimentary extraction of module port names and port mode

    Returns dict() = {'port_name':MODE, ...} where mode: str=input/output/inout
    """
    res = dict()
    with open(infilename, newline='') as infile:
        for row in infile:
            if row == []:
                continue
            #purge trailing comments
            row = row[:row.find('//')]
            #remove end of line comma
            if (',' in row) and (row[-1] == ','):
                row = row[:-1]
            #purge trailing whitespaces
            row = row.lstrip().rstrip()

            if any([sstring in row[:6] for sstring in ['input', 'output', 'inout']]):
                #extract and store data in specification dictionary
                port_name = row.split()[-1]
                port_mode = row[:row.find(' ')]
                res[port_name] = port_mode
    return res
