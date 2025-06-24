# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Murray Ferris, Torsten Reuschel

import pytest


@pytest.hookimpl(optionalhook=True)
def pytest_reporter_context(context):
    """Customize pytest report
    """
    context["title"] = "CAVEAT example: AXIS-FIFO"


if __name__ == '__main__':
    pytest.main([
            '-vra',
            '--template=html-dots/index.html',
            '--report=build/results/report_test_dynamic.html',
        ])
