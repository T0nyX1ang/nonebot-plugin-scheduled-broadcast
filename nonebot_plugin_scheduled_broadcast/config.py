"""The config file."""

from pathlib import Path

from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    """Plugin Config."""

    broadcast_policy_location: Path = Path("./broadcast_policy.json")
