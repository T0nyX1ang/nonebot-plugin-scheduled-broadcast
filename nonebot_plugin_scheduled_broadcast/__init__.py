"""The initialization file."""

import base64
import hashlib
import json
import pickle

import nonebot
from nonebot import on_command, on_fullmatch
from nonebot.adapters import Event, Message
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from nonebot_plugin_scheduled_broadcast.config import Config

__plugin_meta__ = PluginMetadata(
    name="定时广播插件",
    description="一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件.",
    usage="提供超级用户指令: 启动广播/enablebc, 关闭广播/disablebc 广播ID, 提供装饰器: broadcast.",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)
config.broadcast_policy_location.touch(exist_ok=True)  # create the policy file if not exists

anchor_enable = on_fullmatch(msg=('启动广播', 'enablebc'), permission=SUPERUSER)
anchor_disable = on_command(cmd='关闭广播', aliases={'disablebc'}, permission=SUPERUSER)


def load_broadcast_db() -> dict:
    """Load the broadcast policy database."""
    with open(config.broadcast_policy_location, 'r', encoding='utf-8') as f:
        fin = f.read()
        broadcast_db = json.loads(fin) if fin else {}
    return broadcast_db


def save_broadcast_db(content: dict) -> None:
    """Save the broadcast policy database."""
    with open(config.broadcast_policy_location, 'w', encoding='utf-8') as f:
        fout = json.dumps(content, indent=4, ensure_ascii=False, sort_keys=True)
        f.write(fout)


@anchor_enable.handle()
async def handle_anchor_enable(event: Event):
    """Handle the anchor_enable command."""
    self_id = str(event.self_id)
    event_dump = pickle.dumps(event)
    broadcast_id = hashlib.sha256(event_dump).hexdigest()
    event_entry = {"config": {}, "edata": base64.b64encode(event_dump).decode()}

    try:
        broadcast_db = load_broadcast_db()
    except Exception:
        logger.error("Failed to load broadcast policy database.")
        await anchor_enable.finish("广播启动失败, 请检查配置文件是否损坏或者格式错误.")

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

    try:
        broadcast_db = load_broadcast_db()
    except Exception:
        logger.error("Failed to load broadcast policy database.")
        await anchor_enable.finish("广播关闭失败, 请检查配置文件是否损坏或者格式错误.")

    if self_id not in broadcast_db:
        await anchor_disable.finish("该机器人没有启动任何广播.")

    if broadcast_id not in broadcast_db[self_id]:
        await anchor_disable.finish("该广播ID不存在, 请检查输入是否正确.")

    broadcast_db[self_id].pop(broadcast_id)
    save_broadcast_db(broadcast_db)

    await anchor_disable.finish("已关闭广播, 重新启动该功能需要重新进行广播配置.")
