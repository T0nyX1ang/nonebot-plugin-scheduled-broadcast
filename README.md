# <div align="center"> Nonebot Plugin Scheduled Broadcast </div>

<p align="center">
  <a href="https://pypi.python.org/pypi/nonebot-plugin-scheduled-broadcast">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-scheduled-broadcast.svg?color=blue" alt="pypi">
  </a>
  <a href="https://codecov.io/gh/T0nyX1ang/nonebot-plugin-scheduled-broadcast" >
    <img src="https://codecov.io/gh/T0nyX1ang/nonebot-plugin-scheduled-broadcast/graph/badge.svg?token=AUFO081ZBW"/>
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/T0nyX1ang/nonebot-plugin-scheduled-broadcast.svg?color=blue" alt="license">
  </a>
</p>

<div align="center"> ✨ 一款可配置的, 不依赖具体适配器的, 基于事件的定时广播插件. ✨ </div>

## 特性

* 基于一般事件 `nonebot.adapters.Event` 构造, 从而支持全部协议的信息发送.
* 定时广播由文件配置, 基于 `apscheduler` 提供类 `crontab` 的配置参数.

## 安装

### 使用 `nb-cli` 安装

* 在 `nonebot2` 项目的根目录下打开命令行, 输入以下指令即可安装:

```bash
    nb-cli plugin install nonebot-plugin-scheduled-broadcast
```

### 使用包管理器安装

* 使用 `pdm` 安装:

```bash
    pdm add nonebot-plugin-scheduled-broadcast
```

* 使用 `poetry` 安装:

```bash
    poetry add nonebot-plugin-scheduled-broadcast
```

* 使用 `pip` 安装: ~~(虽然不太推荐但大概率没事)~~

```bash
    pip install nonebot-plugin-scheduled-broadcast
```

## 使用

### 启动广播

* 保证发送消息的 `id` 位于 `SUPERUSER` 用户组中.
* 在需要启动广播的地方发送:

```txt
    启动广播/enablebc [广播ID]
```

* `广播ID` 是可选项, 如果用户没有输入 `广播ID`, 则会使用对应事件的 `session_id` 去掉 `user_id` 的结果作为 `广播ID`, 如果此时 `广播ID` 为空, 则不支持自动生成 `广播ID`.
* 如果是第一次使用, 机器人在执行上述命令后, 在 `nonebot2` 项目的根目录下生成一个名为 `broadcast_policy.json` 的配置文件.
* 如果该机器人下已经存在相同的 `广播ID`, 配置文件将会保留, 同时广播作业将被 `恢复`, 如果不需要修改 `config` 中的内容, 不需要重启.

### 配置文件的填写

* 一般而言, 配置文件的结构如下:

```json
{
    "self_id": {
        "broadcast_id": {
            "config": {
                "example": {"second": "*/30"}
            },
            "data": "event data (b64encode)",
            "hash": "event hash (sha256)",
            "enable": true
        },
        "another broadcast_id": {
            // ...
        }
    },
    "another self_id": {
        // ...
    }
}
```

* `config` 的可用配置与 `apscheduler` 一致, 以下给出一个示例, 该示例表示, `example` 命令会在每天 `10:24`, 每隔 `10` 秒被触发:

```json
{
    "config": {
        "example": {
            "hour": 10,
            "minute": 24,
            "second": "*/10"
        }
    }
}
```

* 在准备好了配置文件后, 就可以准备编写待触发的指令了.

### 待触发指令的编写

* 由于本插件提供了一个装饰器, 可以按照如下方式编写待触发指令:

```python
from nonebot import require
from nonebot.adapters import Event
from nonebot.log import logger

require("nonebot_plugin_scheduled_broadcast")

from nonebot_plugin_scheduled_broadcast.core import broadcast

@broadcast('example')
async def _(self_id: str, event: Event):
    """Scheduled example broadcast."""
    message = generate_your_message()
    try:
        bot = nonebot.get_bots()[self_id]  # select the target bot
        await bot.send(event=event, message=message)  # send message
    except Exception:
        logger.error(traceback.format_exc())  # print logs
```

* 触发指令编写完成以后, 重新启动机器人即可.

### 关闭广播

* 保证发送消息的 `id` 位于 `SUPERUSER` 用户组中.
* 在需要关闭广播的地方发送:

```txt
    关闭广播/disablebc [广播ID]
```

* `广播ID` 是可选项, 如果用户没有输入 `广播ID`, 则会使用对应事件的 `session_id` 去掉 `user_id` 的结果作为 `广播ID`, 如果此时 `广播ID` 为空, 则不支持自动生成 `广播ID`.
* 停止广播之后, 对应 `广播ID` 中的 `enable` 将被置为 `false`, 为保持可复用性, 其余部分将不会改变, 同时广播作业将被 `暂停`, 如果不需要修改 `config` 中的内容, 不需要重启.

## 配置

* `broadcast_policy_location`: 代表配置文件的存放位置, 默认值为 `./broadcast_policy.json`

## 注意事项

* 由于每一个 `Event` 几乎不会相同, 建议不要在同一个地方多次执行 `启动广播` 命令, 可能会刷屏的.
* 由于用到了 `pickle` 的序列化和反序列化功能, 而该功能具有潜在的安全风险, **请谨慎对待来源不明的配置文件**. 如果不确定配置文件的安全性, 建议重新启动广播以生成新的 `广播ID`, 然后替换配置文件中的 `config` 键里面的内容.
* 由于配置文件的生成限制, 当修改了 `config` 中的内容时, 必须需要重启机器人使得新的配置生效, 其它情况下均不需要重启机器人.

## 协议

* 本项目使用 [MIT](./LICENSE) 协议
