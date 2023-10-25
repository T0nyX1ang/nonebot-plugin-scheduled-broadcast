"""The initialization file."""

from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from .config import Config
from .core import load_broadcast_db, save_broadcast_db, dump_event, pause_target_jobs, resume_target_jobs

__plugin_meta__ = PluginMetadata(
    name="定时广播插件",
    description="一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件.",
    usage="超级用户指令:\n启动广播/enablebc 广播ID,\n关闭广播/disablebc 广播ID\n装饰器: broadcast",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)

anchor_enable = on_command(cmd="启动广播", aliases={"enablebc"}, permission=SUPERUSER)
anchor_disable = on_command(cmd="关闭广播", aliases={"disablebc"}, permission=SUPERUSER)


@anchor_enable.handle()
async def handle_anchor_enable(bot: Bot, event: Event, arg: Message = CommandArg()):
    """Handle the anchor_enable command."""
    self_id = str(bot.self_id)
    broadcast_id = arg.extract_plain_text().strip()
    if not broadcast_id:
        await anchor_enable.finish("广播ID不能为空")

    event_data, event_hash = dump_event(event)

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        broadcast_db[self_id] = {}

    if broadcast_id not in broadcast_db[self_id]:
        broadcast_db[self_id][broadcast_id] = {}
        broadcast_db[self_id][broadcast_id]["config"] = {}
        broadcast_db[self_id][broadcast_id]["data"] = event_data
        broadcast_db[self_id][broadcast_id]["hash"] = event_hash

    broadcast_db[self_id][broadcast_id]["enable"] = True  # enable the broadcast
    save_broadcast_db(broadcast_db)
    resume_target_jobs(self_id, broadcast_id)

    await anchor_enable.finish(f"已启动广播, 广播ID为{broadcast_id}, 请进行广播配置, 需要删除广播时请使用关闭广播+广播ID")


@anchor_disable.handle()
async def handle_anchor_disable(bot: Bot, arg: Message = CommandArg()):
    """Handle the anchor_disable command."""
    self_id = str(bot.self_id)
    broadcast_id = arg.extract_plain_text().strip()

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        await anchor_disable.finish("该机器人没有启动任何广播")

    if broadcast_id not in broadcast_db[self_id]:
        await anchor_disable.finish("该广播ID不存在, 请检查输入是否正确")

    broadcast_db[self_id][broadcast_id]["enable"] = False  # disable the broadcast
    save_broadcast_db(broadcast_db)
    pause_target_jobs(self_id, broadcast_id)

    await anchor_disable.finish("已关闭广播")
