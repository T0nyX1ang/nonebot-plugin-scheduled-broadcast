"""A command to create an anchor message."""

import base64
import hashlib
import json
import pickle

import nonebot
from nonebot import on_fullmatch, on_command
from nonebot.adapters import Event, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from nonebot_plugin_scheduled_broadcast.config import Config

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

anchor_enable = on_fullmatch(msg=('启动广播', 'enablebc'), permission=SUPERUSER)
anchor_disable = on_command(cmd=('关闭广播', 'disablebc'), permission=SUPERUSER)


@anchor_enable.handle()
async def handle_anchor_enable(event: Event):
    """Handle the anchor_enable command."""
    self_id = str(event.self_id)
    event_dump = pickle.dumps(event)
    broadcast_id = hashlib.sha256(event_dump).hexdigest()
    event_entry = {broadcast_id: {"config": {}, "edata": base64.b64encode(event_dump).decode()}}

    with open(config.broadcast_policy_location, 'r', encoding='utf-8') as f:
        broadcast_db = json.load(f)

    if self_id not in broadcast_db:
        broadcast_db[self_id] = {}

    broadcast_db[self_id] = event_entry

    with open(config.broadcast_policy_location, 'w', encoding='utf-8') as f:
        json.dump(broadcast_db, f, indent=4, ensure_ascii=False, sort_keys=True)

    await anchor_enable.finish(f"已启动广播, 广播ID为{event_entry['hash']}, 请进行广播配置, 需要删除广播时请使用关闭广播+广播ID")


@anchor_disable.handle()
async def handle_anchor_disable(event: Event, arg: Message = CommandArg()):
    """Handle the anchor_enable command."""
    self_id = str(event.self_id)
    broadcast_id = arg.extract_plain_text().strip()

    with open(config.broadcast_policy_location, 'r', encoding='utf-8') as f:
        broadcast_db = json.load(f)

    if self_id not in broadcast_db:
        await anchor_disable.finish("该机器人没有启动任何广播.")

    if broadcast_id in broadcast_db[self_id]:
        broadcast_db[self_id].pop(broadcast_id)
        await anchor_disable.finish("已关闭广播, 重新启动该功能需要重新进行广播配置.")
    else:
        await anchor_disable.finish("该广播ID不存在, 请检查输入是否正确.")
