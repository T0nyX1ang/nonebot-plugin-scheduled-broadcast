"""The initialization file."""

from argparse import Namespace

from nonebot import on_shell_command
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.params import Depends, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import ArgumentParser

from .config import Config
from .core import (
    dump_event,
    load_broadcast_db,
    pause_all_jobs,
    resume_all_jobs,
    modify_target_job,
    save_broadcast_db,
)
from .db import BroadcastBotDB, BroadcastConfig, SchedulerConfig

__plugin_meta__ = PluginMetadata(
    name="定时广播插件",
    description="一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件.",
    usage="""超级用户指令:
                启动广播/enablebc [-bid 广播ID],
                关闭广播/disablebc [-bid 广播ID],
                设置广播/setbc 待触发指令 [-bid 广播ID] [-s 秒] [-m 分] [-h 时] [-w 周数] [-d 星期几] [-D 日] [-M 月] [-Y 年]
             装饰器:
                @broadcast("待触发指令")""",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)

bid_receiver = ArgumentParser(add_help=False)
bid_receiver.add_argument("-bid", "--broadcast-id", default="")
anchor_enable = on_shell_command(cmd="启动广播", aliases={"enablebc"}, parser=bid_receiver, permission=SUPERUSER)
anchor_disable = on_shell_command(cmd="关闭广播", aliases={"disablebc"}, parser=bid_receiver, permission=SUPERUSER)

set_scheduler_parser = ArgumentParser(add_help=False)
set_scheduler_parser.add_argument("broadcast_command")
set_scheduler_parser.add_argument("-bid", "--broadcast-id", default="")
set_scheduler_parser.add_argument("-s", "--second")
set_scheduler_parser.add_argument("-m", "--minute")
set_scheduler_parser.add_argument("-h", "--hour")
set_scheduler_parser.add_argument("-w", "--week")
set_scheduler_parser.add_argument("-d", "--day-of-week")
set_scheduler_parser.add_argument("-D", "--day")
set_scheduler_parser.add_argument("-M", "--month")
set_scheduler_parser.add_argument("-Y", "--year")
anchor_setting = on_shell_command(cmd="设置广播", aliases={"setbc"}, parser=set_scheduler_parser, permission=SUPERUSER)


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
    resume_all_jobs(self_id, broadcast_id)

    await anchor_enable.finish(f"已启动ID为{broadcast_id}的广播")


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
    pause_all_jobs(self_id, broadcast_id)

    await anchor_disable.finish(f"已关闭ID为{broadcast_id}的广播")


@anchor_setting.handle()
async def handle_anchor_setting(
    bot: Bot, broadcast_id: str = Depends(extract_broadcast_id), arg: Namespace = ShellCommandArgs()
):
    """Handle the anchor_setting command."""
    self_id = str(bot.self_id)
    if not broadcast_id:
        await anchor_setting.finish("广播ID不能为空")

    broadcast_db = load_broadcast_db()
    cmd_name = str(arg.broadcast_command)
    try:
        broadcast_db[self_id][broadcast_id].config[cmd_name] = SchedulerConfig(
            second=arg.second,
            minute=arg.minute,
            hour=arg.hour,
            week=arg.week,
            day_of_week=arg.day_of_week,
            day=arg.day,
            month=arg.month,
            year=arg.year,
        )
        modify_target_job(self_id, broadcast_id, cmd_name)
        save_broadcast_db(broadcast_db)
        await anchor_setting.send(f"已设置广播ID为{broadcast_id}, 指令为{cmd_name}的广播")
    except Exception:
        await anchor_setting.finish("广播ID不存在或者参数配置错误, 请检查输入是否正确")
