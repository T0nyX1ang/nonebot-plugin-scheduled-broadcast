"""The test config file."""

import nonebot
import pytest
from nonebug import NONEBOT_INIT_KWARGS

# from . import TestAdapter


def pytest_configure(config: pytest.Config):
    """Configure pytest."""
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~none",
        "log_level": "DEBUG",
        "command_start": [""],
        "use_headless_mode": True,
        "superusers": ["TestSuperUser"],
    }


@pytest.fixture(scope="session", autouse=True)
def load_bot() -> None:
    """Load the bot."""
    nonebot.require("nonebot_plugin_scheduled_broadcast")
