# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import warnings


def escalate_warnings_from_cocotb_log(caplog):
    """Extract list of warning messages from cocotb test and escalate them for
    processing at parent level, e.g. pytest
    """
    for record in caplog.records:
        if 'WARNING' in record.message.upper():
            warnings.warn(record.message)
