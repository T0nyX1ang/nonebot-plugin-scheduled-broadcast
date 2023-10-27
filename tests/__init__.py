"""
The test initialization file.

A test adapter with bot and event is created here.
"""

from typing import Iterable, Type, Union

from nonebot.adapters import Event as BaseEvent
from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from typing_extensions import override


class TestMsgSeg(BaseMessageSegment["TestMsg"]):
    """A simple message segment for tests."""

    @classmethod
    @override
    def get_message_class(cls) -> Type["TestMsg"]:
        return TestMsg

    @override
    def __str__(self) -> str:
        return self.data["text"]

    @override
    def is_text(self) -> bool:
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "TestMsgSeg":
        """Create a text message segment."""
        return TestMsgSeg("text", {"text": text})


class TestMsg(BaseMessage[TestMsgSeg]):
    """A simple message for tests."""

    @classmethod
    @override
    def get_segment_class(cls) -> Type[TestMsgSeg]:
        return TestMsgSeg

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[TestMsgSeg]:
        yield TestMsgSeg.text(msg)


class TestMsgEvent(BaseEvent):
    """A simple message event for tests."""

    user_id: str
    message: Union[str, TestMsg, TestMsgSeg]
    post_type: str = "message"
    location: str = ""

    @override
    def get_type(self) -> str:
        return self.post_type

    @override
    def get_event_name(self) -> str:
        return self.post_type

    @override
    def get_event_description(self) -> str:
        return str(self.dict())

    @override
    def get_message(self) -> TestMsg:
        return TestMsg(self.message)

    @override
    def get_user_id(self) -> str:
        return self.user_id

    @override
    def get_session_id(self) -> str:
        return f"{self.location}{self.user_id}"

    @override
    def is_tome(self) -> bool:
        """Return whether the event is to the bot."""
        return True
