"""Database storage for scheduled broadcast plugin."""

from typing import Dict, Iterator, List, Union

from pydantic import BaseModel, Extra, Field  # pylint: disable=no-name-in-module


class SchedulerConfig(BaseModel, extra=Extra.allow):
    """The model for a specific apscheduler config."""

    second: Union[int, str, None] = None
    minute: Union[int, str, None] = None
    hour: Union[int, str, None] = None
    week: Union[int, str, None] = None
    day_of_week: Union[int, str, None] = None
    day: Union[int, str, None] = None
    month: Union[int, str, None] = None
    year: Union[int, str, None] = None


class BroadcastConfig(BaseModel, extra=Extra.allow):
    """The model for a specific broadcast config."""

    config: Dict[str, SchedulerConfig]
    enable: bool
    data: str
    hash: str
    valid_commands: List[str] = Field(default=[], exclude=True)


class BroadcastBotDB(BaseModel, extra=Extra.allow):
    """The model for a broadcast id under the same bot with broadcast config."""

    __root__: Dict[str, BroadcastConfig]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__root__)

    def __getitem__(self, item: str) -> BroadcastConfig:
        return self.__root__[item]

    def __setitem__(self, item: str, value: BroadcastConfig) -> None:
        self.__root__[item] = value


class BroadcastDB(BaseModel, extra=Extra.allow):
    """The broadcast database under different bots."""

    __root__: Dict[str, BroadcastBotDB]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__root__)

    def __getitem__(self, item: str) -> BroadcastBotDB:
        return self.__root__[item]

    def __setitem__(self, item: str, value: BroadcastBotDB) -> None:
        self.__root__[item] = value
