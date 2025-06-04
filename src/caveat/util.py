# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import re
import warnings


def escalate_warnings_from_cocotb_log(caplog):
    """Extract list of warning messages from cocotb test and escalate them for
    processing at parent level, e.g. pytest
    """
    for record in caplog.records:
        if 'WARNING' in record.message.upper():
            #remove color formatting (may be enabled by use of COCOTB_ANSI_OUTPUT)
            cleaned_message = re.sub(r'\[[0-9]*m', ' ', record.message)
            warnings.warn(cleaned_message)
