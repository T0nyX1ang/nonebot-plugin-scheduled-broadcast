"""Database storage for scheduled broadcast plugin."""

from typing import Dict, Union, Iterator

from pydantic import BaseModel, Extra  # pylint: disable=no-name-in-module


class BroadcastConfig(BaseModel, extra=Extra.allow):
    """The model for a specific broadcast config."""

    config: Dict[str, Dict[str, Union[int, str]]]
    enable: bool
    data: str
    hash: str


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
