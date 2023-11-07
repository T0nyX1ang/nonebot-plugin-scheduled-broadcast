"""Test the commands in this module."""

import pathlib

import nonebot
import pytest
from nonebug import App

from . import TestMsg, TestMsgEvent

if pathlib.Path("broadcast_policy.json").exists():
    pathlib.Path("broadcast_policy.json").unlink()

pathlib.Path("broadcast_policy.json").touch(exist_ok=True)
pathlib.Path("broadcast_policy.json").write_text("Not a json file.", encoding="utf-8")


@pytest.fixture(scope="session", autouse=True)
def load_bot() -> None:
    """Load the bot."""
    try:
        nonebot.require("nonebot_plugin_scheduled_broadcast")
        assert False
    except Exception:
        pathlib.Path("broadcast_policy.json").unlink()
        assert True


def make_event(message: str, user_id: str = "TestUser", location: str = "") -> TestMsgEvent:
    """Make a MessageEvent."""
    return TestMsgEvent(message=TestMsg(message), user_id=user_id, location=location)


@pytest.mark.asyncio
async def test_broadcast_command(app: App):
    """Test the broadcast command."""
    from nonebot_plugin_scheduled_broadcast import (  # pylint: disable=import-outside-toplevel
        anchor_enable,
        load_broadcast_db,
    )

    from nonebot_plugin_scheduled_broadcast.core import (  # pylint: disable=import-outside-toplevel
        load_event,
    )

    normal_user_enable_bid = make_event("enablebc --broadcast-id testid")
    enable_without_bid = make_event("enablebc", user_id="TestSuperUser")
    enable_missing_param = make_event("enablebc -bid", user_id="TestSuperUser")
    enable_with_bid = make_event("enablebc --broadcast-id testid", user_id="TestSuperUser")
    enable_with_location = make_event("enablebc", user_id="TestSuperUser", location="TestLocation")

    async with app.test_matcher(anchor_enable) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, normal_user_enable_bid)
        ctx.should_not_pass_permission()

        ctx.receive_event(bot, enable_without_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(enable_without_bid, "广播ID不能为空")

        ctx.receive_event(bot, enable_missing_param)
        ctx.should_pass_permission()
        # ctx.should_call_send(enable_missing_param, "")

        ctx.receive_event(bot, enable_with_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(enable_with_bid, "已启动ID为testid的广播")

        ctx.receive_event(bot, enable_with_location)
        ctx.should_pass_permission()
        ctx.should_call_send(enable_with_location, "已启动ID为TestLocation的广播")

        assert pathlib.Path("broadcast_policy.json").exists()

    db = load_broadcast_db()
    assert db["TestBot"]["testid"].enable is True
    assert db["TestBot"]["testid"].config == {}
    assert db["TestBot"]["TestLocation"].enable is True
    assert db["TestBot"]["TestLocation"].config == {}

    recovered_event = load_event(db["TestBot"]["testid"].data, db["TestBot"]["testid"].hash)
    assert recovered_event.get_message() == TestMsg("enablebc --broadcast-id testid")
    assert recovered_event.get_user_id() == "TestSuperUser"
    assert recovered_event.get_session_id() == "TestSuperUser"

    recovered_event = load_event(db["TestBot"]["TestLocation"].data, db["TestBot"]["TestLocation"].hash)
    assert recovered_event.get_message() == TestMsg("enablebc")
    assert recovered_event.get_user_id() == "TestSuperUser"
    assert recovered_event.get_session_id() == "TestLocationTestSuperUser"


@pytest.mark.asyncio
async def test_disable_broadcast_command(app: App):
    """Test the broadcast command."""
    from nonebot_plugin_scheduled_broadcast import (  # pylint: disable=import-outside-toplevel
        anchor_disable,
        load_broadcast_db,
    )

    normal_user_disable_bid = make_event("disablebc -bid testid")
    disable_without_bid = make_event("disablebc", user_id="TestSuperUser")
    disable_with_fake_bid = make_event("disablebc -bid fakeid", user_id="TestSuperUser")
    disable_with_bid = make_event("disablebc -bid testid", user_id="TestSuperUser")
    disable_with_location = make_event("disablebc", user_id="TestSuperUser", location="TestLocation")

    async with app.test_matcher(anchor_disable) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, normal_user_disable_bid)
        ctx.should_not_pass_permission()

        ctx.receive_event(bot, disable_without_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_without_bid, "该广播ID不存在, 请检查输入是否正确")

        ctx.receive_event(bot, disable_with_fake_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_with_fake_bid, "该广播ID不存在, 请检查输入是否正确")

        ctx.receive_event(bot, disable_with_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_with_bid, "已关闭ID为testid的广播")

        ctx.receive_event(bot, disable_with_location)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_with_location, "已关闭ID为TestLocation的广播")

    db = load_broadcast_db()
    assert db["TestBot"]["testid"].enable is False
    assert db["TestBot"]["testid"].config == {}
    assert db["TestBot"]["TestLocation"].enable is False
    assert db["TestBot"]["TestLocation"].config == {}

    async with app.test_matcher(anchor_disable) as ctx:
        bot = ctx.create_bot(self_id="FakeBot")
        ctx.receive_event(bot, disable_with_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_with_bid, "该机器人没有启动任何广播")


@pytest.mark.asyncio
async def test_broadcast_function(app: App):
    """Test the broadcast function."""
    from nonebot_plugin_apscheduler import (  # pylint: disable=import-outside-toplevel
        scheduler,
    )

    from nonebot_plugin_scheduled_broadcast import (  # pylint: disable=import-outside-toplevel
        anchor_disable,
        anchor_enable,
        anchor_setting,
    )
    from nonebot_plugin_scheduled_broadcast.core import (  # pylint: disable=import-outside-toplevel
        broadcast,
        load_broadcast_db,
    )

    enable_with_bid = make_event("enablebc --broadcast-id testid", user_id="TestSuperUser")
    disable_with_bid = make_event("disablebc --broadcast-id testid", user_id="TestSuperUser")
    setting_with_bid_valid_cmd = make_event("setbc testcommand -bid testid -m 0", user_id="TestSuperUser")
    resetting_with_bid_valid_cmd = make_event("setbc testcommand -bid testid -m */10", user_id="TestSuperUser")
    setting_with_bid_valid_cmd_2 = make_event(
        "setbc unknowncommand -bid testid -s 45 -h 2 -M 11 -Y 2099", user_id="TestSuperUser"
    )
    setting_with_bid_invalid_cmd = make_event("setbc testcommand", user_id="TestSuperUser")
    setting_with_bid_invalid_cmd_2 = make_event(
        "setbc fakecommand -bid unknownid -s 90 -h 2 -M 11 -Y 2099", user_id="TestSuperUser"
    )

    async with app.test_matcher(anchor_setting) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, setting_with_bid_valid_cmd)
        ctx.should_pass_permission()
        ctx.should_call_send(setting_with_bid_valid_cmd, "已设置广播ID为testid, 指令为testcommand的广播")

        ctx.receive_event(bot, setting_with_bid_valid_cmd_2)
        ctx.should_pass_permission()
        ctx.should_call_send(setting_with_bid_valid_cmd_2, "已设置广播ID为testid, 指令为unknowncommand的广播")

        ctx.receive_event(bot, setting_with_bid_invalid_cmd)
        ctx.should_pass_permission()
        ctx.should_call_send(setting_with_bid_invalid_cmd, "广播ID不能为空")

        ctx.receive_event(bot, setting_with_bid_invalid_cmd_2)
        ctx.should_pass_permission()
        ctx.should_call_send(setting_with_bid_invalid_cmd_2, "广播ID不存在或者参数配置错误, 请检查输入是否正确")

    db = load_broadcast_db()
    db["TestBot"]["testid"].enable = False
    assert db["TestBot"]["testid"].config["testcommand"].minute == 0
    assert db["TestBot"]["testid"].config["unknowncommand"].second == 45
    assert db["TestBot"]["testid"].config["unknowncommand"].hour == 2
    assert db["TestBot"]["testid"].config["unknowncommand"].month == 11
    assert db["TestBot"]["testid"].config["unknowncommand"].year == 2099

    @broadcast("testcommand")
    async def _(self_id: str, event: TestMsgEvent):
        ...  # code will not reach here

    @broadcast("fakecommand")
    async def _(self_id: str, event: TestMsgEvent):
        ...  # code will not reach here

    assert "unknowncommand" not in db["TestBot"]["testid"].valid_commands

    job_ids = [job.id for job in scheduler.get_jobs()]
    assert "broadcast_testid_bot_TestBot_command_testcommand" in job_ids
    assert "broadcast_testid_bot_TestBot_command_fakecommand" not in job_ids

    job = scheduler.get_job("broadcast_testid_bot_TestBot_command_testcommand")
    assert job is not None  # check if job exists before accessing its arguments
    assert job.next_run_time is None
    target_event = job.args[1]
    assert target_event is not None
    assert target_event == enable_with_bid  # check if the event is correctly passed to the job

    async with app.test_matcher(anchor_enable) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, enable_with_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(enable_with_bid, "已启动ID为testid的广播")

    assert db["TestBot"]["testid"].enable is True
    assert "broadcast_testid_bot_TestBot_command_testcommand" in job_ids
    assert "broadcast_testid_bot_TestBot_command_fakecommand" not in job_ids

    job = scheduler.get_job("broadcast_testid_bot_TestBot_command_testcommand")
    assert job is not None  # check if job exists before accessing its arguments
    assert job.next_run_time is not None

    async with app.test_matcher(anchor_disable) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, disable_with_bid)
        ctx.should_pass_permission()
        ctx.should_call_send(disable_with_bid, "已关闭ID为testid的广播")

    assert db["TestBot"]["testid"].enable is False

    async with app.test_matcher(anchor_setting) as ctx:
        bot = ctx.create_bot(self_id="TestBot")
        ctx.receive_event(bot, resetting_with_bid_valid_cmd)
        ctx.should_pass_permission()
        ctx.should_call_send(resetting_with_bid_valid_cmd, "已设置广播ID为testid, 指令为testcommand的广播")

    assert db["TestBot"]["testid"].config["testcommand"].second is None
    assert db["TestBot"]["testid"].config["testcommand"].minute == "*/10"
    assert db["TestBot"]["testid"].config["testcommand"].hour is None

    # false hash
    db["TestBot"]["testid"].hash = db["TestBot"]["testid"].hash[::-1]

    try:

        @broadcast("testcommand")
        async def _(self_id: str, event: TestMsgEvent):
            ...  # code will not reach here

    except ValueError as e:
        assert str(e) == "Event hash mismatch, the data may be corrupted or tampered."
