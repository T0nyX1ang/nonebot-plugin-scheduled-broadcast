"""The initialization file."""

from argparse import Namespace

from nonebot import on_shell_command
from nonebot.adapters import Bot, Event
from nonebot.rule import ArgumentParser
from nonebot.params import ShellCommandArgs, Depends
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .config import Config
from .core import (
    dump_event,
    load_broadcast_db,
    pause_target_jobs,
    resume_target_jobs,
    save_broadcast_db,
)
from .db import BroadcastConfig, BroadcastBotDB

__plugin_meta__ = PluginMetadata(
    name="定时广播插件",
    description="一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件.",
    usage="""超级用户指令:
                启动广播/enablebc [-bid 广播ID],
                关闭广播/disablebc [-bid 广播ID],
             装饰器:
                @broadcast(cmd_name)""",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)

bid_receiver = ArgumentParser(add_help=False)
bid_receiver.add_argument("-bid", "--broadcast-id", default="")

anchor_enable = on_shell_command(cmd="启动广播", aliases={"enablebc"}, parser=bid_receiver, permission=SUPERUSER)
anchor_disable = on_shell_command(cmd="关闭广播", aliases={"disablebc"}, parser=bid_receiver, permission=SUPERUSER)


def extract_broadcast_id(event: Event, arg: Namespace = ShellCommandArgs()) -> str:
    """Extract the broadcast id from an event."""

    arg_text = str(arg.broadcast_id)
    if arg_text:
        return arg_text  # use the input as broadcast id when it is not empty

    user_id = str(event.get_user_id())
    session_id = str(event.get_session_id())
    broadcast_id = session_id.replace(user_id, "")

    if not broadcast_id:
        logger.warning("The broadcast id seems to be empty, please check the input.")

    return broadcast_id


@anchor_enable.handle()
async def handle_anchor_enable(bot: Bot, event: Event, broadcast_id: str = Depends(extract_broadcast_id)):
    """Handle the anchor_enable command."""
    self_id = str(bot.self_id)
    if not broadcast_id:
        await anchor_enable.finish("广播ID不能为空")

    event_data, event_hash = dump_event(event)
    broadcast_config = BroadcastConfig(config={}, enable=True, data=event_data, hash=event_hash)

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        broadcast_db[self_id] = BroadcastBotDB(__root__={})

    if broadcast_id not in broadcast_db[self_id]:
        broadcast_db[self_id][broadcast_id] = broadcast_config

    broadcast_db[self_id][broadcast_id].enable = True  # enable the broadcast
    save_broadcast_db(broadcast_db)
    resume_target_jobs(self_id, broadcast_id)

    await anchor_enable.finish(f"已启动广播, 广播ID为{broadcast_id}, 请进行广播配置, 需要删除广播时请使用关闭广播+广播ID")


@anchor_disable.handle()
async def handle_anchor_disable(bot: Bot, broadcast_id: str = Depends(extract_broadcast_id)):
    """Handle the anchor_disable command."""
    self_id = str(bot.self_id)

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        await anchor_disable.finish("该机器人没有启动任何广播")

    if broadcast_id not in broadcast_db[self_id]:
        await anchor_disable.finish("该广播ID不存在, 请检查输入是否正确")

    broadcast_db[self_id][broadcast_id].enable = False  # disable the broadcast
    save_broadcast_db(broadcast_db)
    pause_target_jobs(self_id, broadcast_id)

    await anchor_disable.finish("已关闭广播")
