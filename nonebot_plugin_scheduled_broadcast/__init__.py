"""The initialization file."""

from nonebot import on_command, on_fullmatch
from nonebot.adapters import Event, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from nonebot_plugin_scheduled_broadcast.config import Config
from nonebot_plugin_scheduled_broadcast.core import load_broadcast_db, save_broadcast_db, dump_event

__plugin_meta__ = PluginMetadata(
    name="定时广播插件",
    description="一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件.",
    usage="提供超级用户指令: 启动广播/enablebc, 关闭广播/disablebc 广播ID, 提供装饰器: broadcast.",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)

anchor_enable = on_fullmatch(msg=('启动广播', 'enablebc'), permission=SUPERUSER)
anchor_disable = on_command(cmd='关闭广播', aliases={'disablebc'}, permission=SUPERUSER)


@anchor_enable.handle()
async def handle_anchor_enable(event: Event):
    """Handle the anchor_enable command."""
    self_id = str(event.self_id)
    event_data, broadcast_id = dump_event(event)
    event_entry = {"config": {}, "edata": event_data}

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        broadcast_db[self_id] = {}

    if broadcast_id not in broadcast_db[self_id]:
        broadcast_db[self_id][broadcast_id] = event_entry

    save_broadcast_db(broadcast_db)

    await anchor_enable.finish(f"已启动广播, 广播ID为{broadcast_id}, 请进行广播配置, 需要删除广播时请使用关闭广播+广播ID")


@anchor_disable.handle()
async def handle_anchor_disable(event: Event, arg: Message = CommandArg()):
    """Handle the anchor_disable command."""
    self_id = str(event.self_id)
    print(self_id)
    broadcast_id = arg.extract_plain_text().strip()

    broadcast_db = load_broadcast_db()
    if self_id not in broadcast_db:
        await anchor_disable.finish("该机器人没有启动任何广播.")

    if broadcast_id not in broadcast_db[self_id]:
        await anchor_disable.finish("该广播ID不存在, 请检查输入是否正确.")

    broadcast_db[self_id].pop(broadcast_id)
    save_broadcast_db(broadcast_db)

    await anchor_disable.finish("已关闭广播, 重新启动该功能需要重新进行广播配置.")
