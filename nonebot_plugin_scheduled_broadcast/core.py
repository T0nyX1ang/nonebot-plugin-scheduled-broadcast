"""Core functions for scheduled broadcast plugin."""

import base64
import hashlib
import pickle
import json
import sys

import nonebot
from nonebot.adapters import Event
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

from nonebot_plugin_scheduled_broadcast.config import Config

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)
config.broadcast_policy_location.touch(exist_ok=True)  # create the policy file if not exists

try:
    with open(config.broadcast_policy_location, 'r', encoding='utf-8') as fi:
        fin = fi.read()
        broadcast_db: dict[str, dict[str, dict[str, dict]]] = json.loads(fin) if fin else {}
except Exception:
    logger.error("Failed to load broadcast policy database, please check it.")
    sys.exit(1)


def load_broadcast_db() -> dict:
    """Load the broadcast policy database."""
    return broadcast_db


def save_broadcast_db(content: dict) -> None:
    """Save the broadcast policy database."""
    with open(config.broadcast_policy_location, 'w', encoding='utf-8') as fo:
        fout = json.dumps(content, indent=4, ensure_ascii=False, sort_keys=True)
        fo.write(fout)


def load_event(event_str: str, event_hash: str) -> Event:
    """Load an event from a base64 string and validate its hash."""
    event_dump = base64.b64decode(event_str.encode())
    if hashlib.sha256(event_dump).hexdigest() != event_hash:
        raise ValueError('Event hash mismatch, the data may be corrupted or tampered.')
    return pickle.loads(event_dump)


def dump_event(event: Event) -> tuple[str, str]:
    """Dump an event into a base64 string with a hash."""
    event_dump = pickle.dumps(event)
    event_hash = hashlib.sha256(event_dump).hexdigest()
    event_b64 = base64.b64encode(event_dump).decode()
    return (event_b64, event_hash)


def valid(command_name: str) -> list[tuple[str, str]]:
    """Get all valid [self_id, broadcast_id] tuple for broadcast policy."""
    return [(self_id, broadcast_id)
            for self_id in broadcast_db.keys()
            for broadcast_id in broadcast_db[self_id].keys()
            if command_name in broadcast_db[self_id][broadcast_id]["config"]]


def broadcast(command_name: str):
    """Check the policy of each broadcast by name."""
    _name = command_name

    def _broadcast(func):
        """Rule wrapper for "broadcast" item in the policy control."""
        logger.debug(f'Checking broadcast: [{_name}].')
        for self_id, broadcast_id in valid(_name):
            event = load_event(broadcast_db[self_id][broadcast_id]['edata'], broadcast_id)
            scheduler.add_job(func=func,
                              args=(self_id, event),
                              trigger='cron',
                              id=f'{_name}_broadcast_{broadcast_id}_bot_{self_id}',
                              misfire_grace_time=30,
                              replace_existing=True,
                              **broadcast_db[self_id][broadcast_id]["config"][_name])
            logger.debug(f'Created broadcast [{broadcast_id}] with bot [{self_id}] for command [{_name}].')

    return _broadcast
