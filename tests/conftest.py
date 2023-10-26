"""The test config file."""

import pytest
from nonebug import NONEBOT_INIT_KWARGS


def pytest_configure(config: pytest.Config):
    """Configure pytest."""
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~none",
        "log_level": "DEBUG",
        "command_start": [""],
        "use_headless_mode": True,
        "superusers": ["TestSuperUser"],
    }
