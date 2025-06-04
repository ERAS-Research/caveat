# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import re
import warnings
import unicodedata


def purge_unicode_control_character(in_string):
    """Remove control characters from a given string
    Adopted from https://stackoverflow.com/a/19016117 under CC BY-SA 3.0
    """
    return ''.join(char for char in in_string if unicodedata.category(char)[0] != 'C')


def escalate_warnings_from_cocotb_log(caplog):
    """Extract list of warning messages from cocotb test and escalate them for
    processing at parent level, e.g. pytest
    """
    for record in caplog.records:
        if 'WARNING' in record.message.upper():
            #remove color formatting (may be enabled by use of COCOTB_ANSI_OUTPUT)
            cleaned_message = purge_unicode_control_character(record.message)
            cleaned_message = re.sub(r'\[[0-9]*m', '', cleaned_message)
            warnings.warn(cleaned_message)
