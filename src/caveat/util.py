# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

import git
import re
import unicodedata
import warnings


def purge_unicode_control_character(in_string) -> str:
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
            #remove color formatting (may be enabled via COCOTB_ANSI_OUTPUT)
            cleaned_message = purge_unicode_control_character(record.message)
            cleaned_message = re.sub(r'\[[0-9]*m', '', cleaned_message)
            warnings.warn(cleaned_message)

def get_git_revision() -> dict:
    """Helper function to extract git revision information from git repository
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        dt = repo.head.object.committed_datetime
        datestamp = "{:%d%m%Y}".format(dt)
        timestamp = "{:%H%M%S}00".format(dt)
        gitcommit = repo.head.object.hexsha[0:7]
        is_dirty = '1' if repo.is_dirty() else '0'
    except e:
        datestamp = '00000000'
        timestamp = '00000000'
        gitcommit = 'fffffff'
        is_dirty = '1'
    return {'datestamp': datestamp,
            'timestamp': timestamp,
            'gitcommit': gitcommit,
            'is_dirty': is_dirty}
