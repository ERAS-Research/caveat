# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Parse netlist specificaton files
"""

import csv
import numpy as np

def read_netspec_from_csv(infilenames: list):
    """Read in schematic/netlist design from pre-parsed and csv-formatted file
    with format:
      pin_name , voltage_max , Rload, input/output/inout
    """
    res = dict()
    for infilename in infilenames:
        with open(infilename, newline='') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for row in lines:
                if row == []:
                    continue
                #purge trailing whitespaces
                for ii in range(len(row)):
                    row[ii] = row[ii].lstrip().rstrip()
                #ensure valid data
                for ii in range(1,len(row[1:])+1):
                    if row[ii] == '':
                        row[ii] = np.nan
                #store data in specification dictionary
                res[row[0]] = {
                        'voltage_max': np.float64(row[1]),
                        'Rload': np.float64(row[2]),
                        'inout': row[3],
                    }
    return res
