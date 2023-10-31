"""Core functions for scheduled broadcast plugin."""

import base64
import hashlib
import pickle
from typing import List, Tuple

import nonebot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from nonebot.adapters import Event
from nonebot.log import logger

from .config import Config
from .db import BroadcastDB

scheduler: AsyncIOScheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler

global_config = nonebot.get_driver().config
config = Config.parse_obj(global_config)

if not config.broadcast_policy_location.is_file():
    config.broadcast_policy_location.touch()  # create the policy file if not exists
    config.broadcast_policy_location.write_text("{}", encoding="utf-8")  # write an empty dict to the policy file

try:
    broadcast_db = BroadcastDB.parse_file(config.broadcast_policy_location)  # load database
except Exception as e:
    logger.error("Failed to load broadcast policy database, please check it.")
    raise e


def load_broadcast_db() -> BroadcastDB:
    """Load the broadcast policy database."""
    return broadcast_db


def save_broadcast_db(content: BroadcastDB) -> None:
    """Save the broadcast policy database."""
    config.broadcast_policy_location.write_text(
        content.json(exclude_defaults=True, indent=4, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )


def load_event(event_str: str, event_hash: str) -> Event:
    """Load an event from a base64 string and validate its hash."""
    event_dump = base64.b64decode(event_str.encode())
    if hashlib.sha256(event_dump).hexdigest() != event_hash:
        raise ValueError("Event hash mismatch, the data may be corrupted or tampered.")
    return pickle.loads(event_dump)


def dump_event(event: Event) -> Tuple[str, str]:
    """Dump an event into a base64 string with a hash."""
    event_dump = pickle.dumps(event)
    event_hash = hashlib.sha256(event_dump).hexdigest()
    event_b64 = base64.b64encode(event_dump).decode()
    return (event_b64, event_hash)


def valid(cmd_name: str) -> List[Tuple[str, str]]:
    """Get all valid [self_id, broadcast_id] tuples for broadcast policy."""
    return [
        (self_id, broadcast_id)
        for self_id in broadcast_db
        for broadcast_id in broadcast_db[self_id]
        if cmd_name in broadcast_db[self_id][broadcast_id].config
    ]


def pause_target_jobs(self_id: str, broadcast_id: str) -> None:
    """Pause the target broadcast jobs."""
    for cmd_name in broadcast_db[self_id][broadcast_id].valid_commands:
        scheduler.pause_job(f"broadcast_{broadcast_id}_bot_{self_id}_command_{cmd_name}")
        logger.debug(f"Paused broadcast [{broadcast_id}] with bot [{self_id}] for command [{cmd_name}].")


def resume_target_jobs(self_id: str, broadcast_id: str) -> None:
    """Resume the target broadcast jobs."""
    for cmd_name in broadcast_db[self_id][broadcast_id].valid_commands:
        scheduler.resume_job(f"broadcast_{broadcast_id}_bot_{self_id}_command_{cmd_name}")
        logger.debug(f"Resumed broadcast [{broadcast_id}] with bot [{self_id}] for command [{cmd_name}].")


def broadcast(cmd_name: str):
    """Check the policy of each broadcast by name."""
    _name = cmd_name

    def _broadcast(func):
        """Rule wrapper for "broadcast" item in the policy control."""
        logger.debug(f"Checking broadcast: [{_name}].")
        for self_id, broadcast_id in valid(_name):
            event_data: str = broadcast_db[self_id][broadcast_id].data
            event_hash: str = broadcast_db[self_id][broadcast_id].hash
            event = load_event(event_data, event_hash)
            scheduler.add_job(
                func=func,
                args=(self_id, event),
                trigger=CronTrigger(**broadcast_db[self_id][broadcast_id].config[_name].dict()),
                id=f"broadcast_{broadcast_id}_bot_{self_id}_command_{_name}",
                misfire_grace_time=30,
                replace_existing=True,
            )
            broadcast_db[self_id][broadcast_id].valid_commands.append(_name)
            logger.debug(f"Created broadcast [{broadcast_id}] with bot [{self_id}] for command [{_name}].")

            if not broadcast_db[self_id][broadcast_id].enable:
                scheduler.pause_job(f"broadcast_{broadcast_id}_bot_{self_id}_command_{_name}")
                logger.debug(f"Paused broadcast [{broadcast_id}] with bot [{self_id}] for command [{_name}].")

    return _broadcast
