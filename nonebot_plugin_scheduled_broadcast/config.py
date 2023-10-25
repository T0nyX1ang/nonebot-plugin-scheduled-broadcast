"""The config file."""

from pathlib import Path

from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    """Plugin Config."""

    broadcast_policy_location: Path = Path("./broadcast_policy.json")
