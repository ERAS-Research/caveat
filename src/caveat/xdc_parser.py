# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
Parse xdc constraint files
"""


def read_xdc(infilenames: list):
    """Read in xdc constraint files
    """
    for infilename in infilenames:
        print(infilename)
    return len(infilenames)
