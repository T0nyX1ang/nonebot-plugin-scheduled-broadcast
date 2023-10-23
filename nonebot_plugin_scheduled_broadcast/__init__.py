"""The initialization file."""

from nonebot.plugin import PluginMetadata

from nonebot_plugin_scheduled_broadcast.config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_scheduled_broadcast",
    description="An event-based scheduled broadcaster aiming for all nonebot2 adapters.",
    usage="启动广播/enablebc, 关闭广播/disablebc 广播ID",
    type="library",
    homepage="https://github.com/T0nyX1ang/nonebot-plugin-scheduled-broadcast",
    config=Config,
)
