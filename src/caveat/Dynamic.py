# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

"""
This module implements building blocks for dynamic, i.e. algorithmic,
verification.
"""


class Dynamic(object):
    """
    Toolbox for dynamic verification
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the device settings before connecting

        @param verbose  The logging mode for verbose output, default false
        """
        self.verbose = verbose
